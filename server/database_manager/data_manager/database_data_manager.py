import pymongo
from pymongo.collection import Collection
from datetime import datetime, timedelta

from server.database_manager.authentication_manager import authentication_manager
from server.database_manager.exception_types import InvalidRequestException
from utilities.decorators.singleton import singleton


@singleton
class DatabaseDataManager(object):
    _users_collection: Collection
    _classes_collection: Collection

    def __init__(self, database_name: str):
        database_client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = database_client[database_name]
        self._users_collection = database["users"]
        self._classes_collection = database["classes"]

    def get_user_by_name(self, username: str):
        query = {'username': username}
        return self._users_collection.find_one(query)

    def get_user_by_id(self, user_id: str):
        query = {'id': user_id}
        return self._users_collection.find_one(query)

    def get_class_by_name(self, class_name: str):
        query = {'name': class_name}
        return self._classes_collection.find_one(query)

    def get_class_by_id(self, class_id: str):
        query = {'class_id': class_id}
        return self._classes_collection.find_one(query)

    def get_classes_by_username(self, username: str):
        user_doc = self.get_user_by_name(username)
        classes = [self.get_class_by_id(class_id) for class_id in user_doc['classes']]
        for class_doc in classes:
            class_doc.pop('_id')
        return classes

    def insert_user(self, user_data: dict):
        if self.user_exists(user_data['username']):
            raise InvalidRequestException('Username {} already exists'.format(user_data['username']))
        hashed_password = authentication_manager.AuthenticationManager.get_hashed_password(user_data['password'])
        query = user_data
        query['password'] = hashed_password
        return self._users_collection.insert_one(query)

    def remove_user(self, username: str):
        query = {'username': username}
        self._users_collection.delete_one(query)

    def insert_class(self, class_data: dict):
        if self.class_exists(class_data['class_name']):
            raise InvalidRequestException('Class {} already exists'.format(class_data['class_name']))
        if 'participants' in class_data:
            for participant in class_data['participants']:
                if not self.user_exists(participant):
                    raise InvalidRequestException('User does not exist: {}'.format(participant))
        if not self.user_exists(class_data['teacher']):
            raise InvalidRequestException('Teacher user {} does not exist'.format(class_data['teacher']))
        if not self.is_teacher(class_data['teacher']):
            raise InvalidRequestException('User {} cannot be teacher'.format(class_data['teacher']))
        new_id = self.create_id()
        class_data['class_id'] = new_id
        self._classes_collection.insert_one(class_data)

    def add_participant(self, username: str, class_name: str):
        if not self.class_exists(class_name):
            raise InvalidRequestException('class {} does not exist'.format(class_name))
        if not self.user_exists(username):
            raise InvalidRequestException('user {} does not exist'.format(username))
        if self.user_participating_class(username, class_name):
            raise InvalidRequestException('user {} already participating class'.format(username))
        self._classes_collection.find_one_and_update({'name': class_name}, {'$push': {'participants': username}})

    def remove_participant(self, username: str, class_name: str):
        if not self.class_exists(class_name):
            raise InvalidRequestException('class {} does not exist'.format(class_name))
        if not self.user_exists(username):
            raise InvalidRequestException('user {} does not exist'.format(username))
        if not self.user_participating_class(username, class_name):
            raise InvalidRequestException('user {} is not participating class'.format(username))
        self._classes_collection.find_one_and_update({'name': class_name}, {'$pull': {'participants': username}})

    def user_exists(self, username: str):
        return self._users_collection.count_documents({'username': username}, limit=1) != 0

    def class_exists(self, class_name: str):
        return self._classes_collection.count_documents({'name': class_name}, limit=1) != 0

    def user_participating_class(self, username: str, class_name: str):
        if not self.class_exists(class_name):
            return False
        user_query = {'name': class_name, 'participants': {'$all': [username]}}
        teacher_query = {'name': class_name, 'teacher': username}
        return (self._classes_collection.find(user_query).count() == 1 or
                self._classes_collection.find(teacher_query).count() == 1)

    def is_teacher(self, username: str):
        if not self.user_exists(username):
            return False
        teacher_query = {'username': username, 'role': 'teacher'}
        return self._users_collection.find(teacher_query).count() == 1

    def update_user(self, username: str, update_info: dict):
        if not self.user_exists(username):
            raise InvalidRequestException('user {} does not exist'.format(username))
        for key in update_info:
            self._users_collection.find_one_and_update({'username': username}, {'$set': {key: update_info[key]}})

    def update_class(self, class_name: str, update_info: dict):
        if not self.class_exists(class_name):
            raise InvalidRequestException('class {} does not exist'.format(class_name))
        for key in update_info:
            self._classes_collection.find_one_and_update({'name': class_name}, {'$set': {key: update_info[key]}})

    def login_user(self, username: str):
        time_now = datetime.now()
        parsed_time = time_now.strftime("%m/%d/%Y, %H:%M:%S")
        self._users_collection.find_one_and_update({'username': username}, {'$set': {'last_login': parsed_time}})

    def check_if_user_logged_in(self, username: str, hours_since=0, minutes_since=60, seconds_since=0):
        time_now = datetime.now()
        user_document = self.get_user_by_name(username)
        if 'last_login' not in user_document:
            return False
        last_login = datetime.strptime(user_document['login'], "%m/%d/%Y, %H:%M:%S")
        if time_now < last_login + timedelta(hours=hours_since, minutes=minutes_since, seconds=seconds_since):
            return True
        return False

    def create_id(self):
        next_id = 1
        for class_doc in self._classes_collection.find():
            class_id = int(class_doc['class_id'])
            if class_id > next_id:
                next_id = class_id
        return str(next_id + 1)
