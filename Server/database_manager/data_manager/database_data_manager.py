import pymongo

from Server.database_manager.exception_types import InvalidRequestException
from Server.database_manager.authentication_manager import authentication_manager


class DatabaseDataManager:
    def __init__(self, database_name):
        database_client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = database_client[database_name]
        self.users_collection = database["users"]
        self.classes_collection = database["classes"]

    def get_user_by_name(self, username):
        query = {'username': username}
        return self.users_collection.find_one(query)

    def get_class_by_name(self, class_name):
        query = {'name': class_name}
        return self.classes_collection.find_one(query)

    def insert_user(self, username, password, details):
        if self.user_exists(username):
            raise InvalidRequestException('Username {} already exists'.format(username))
        hashed_password = authentication_manager.AuthenticationManager.get_hashed_password(password)
        query = {'username': username, 'password': hashed_password, 'details': details}
        return self.users_collection.insert_one(query)

    def remove_user(self, username):
        query = {'username': username}
        self.users_collection.delete_one(query)

    def insert_class(self, class_name, teacher_username, details, participants=None):
        if self.class_exists(class_name):
            raise InvalidRequestException('Class with the same name {} already exists'.format(class_name))
        if not self.user_exists(teacher_username):
            raise InvalidRequestException('Teacher user {} does not exist'.format(teacher_username))
        query = {'name': class_name, 'teacher': teacher_username, 'details': details, 'participants': []}
        if participants is not None:
            for participant in participants:
                if not self.user_exists(participant):
                    raise InvalidRequestException('User does not exist: {}'.format(participant))
            query['participants'] = participants
        return self.classes_collection.insert_one(query)

    def add_participant(self, username, class_name):
        if not self.class_exists(class_name):
            raise InvalidRequestException('class {} does not exist'.format(class_name))
        if not self.user_exists(username):
            raise InvalidRequestException('user {} does not exist'.format(username))
        if self.user_participating_class(username, class_name):
            raise InvalidRequestException('user {} already participating class'.format(username))
        self.classes_collection.find_one_and_update({'name': class_name}, {'$push': {'participants': username}})

    def remove_participant(self, username, class_name):
        if not self.class_exists(class_name):
            raise InvalidRequestException('class {} does not exist'.format(class_name))
        if not self.user_exists(username):
            raise InvalidRequestException('user {} does not exist'.format(username))
        if not self.user_participating_class(username, class_name):
            raise InvalidRequestException('user {} is not participating class'.format(username))
        self.classes_collection.find_one_and_update({'name': class_name}, {'$pull': {'participants': username}})

    def user_exists(self, username):
        return self.users_collection.count_documents({'username': username}, limit=1) != 0

    def class_exists(self, class_name):
        return self.classes_collection.count_documents({'name': class_name}, limit=1) != 0

    def user_participating_class(self, username, class_name):
        if not self.class_exists(class_name):
            return False
        user_query = {'name': class_name, 'participants': {'$all': [username]}}
        teacher_query = {'name': class_name, 'teacher': username}
        return self.classes_collection.find(user_query).count() == 1 \
            or self.classes_collection.find(teacher_query).count() == 1

    def is_teacher(self, username, class_name):
        if not self.class_exists(class_name):
            return False
        teacher_query = {'name': class_name, 'teacher': username}
        return self.classes_collection.find(teacher_query).count() == 1

    def update_user(self, username, update_info):
        if not self.user_exists(username):
            raise InvalidRequestException('user {} does not exist'.format(username))
        for key in update_info:
            self.users_collection.find_one_and_update({'username': username}, {'$set': {key: update_info[key]}})

    def update_class(self, class_name, update_info):
        if not self.class_exists(class_name):
            raise InvalidRequestException('class {} does not exist'.format(class_name))
        for key in update_info:
            self.classes_collection.find_one_and_update({'name': class_name}, {'$set': {key: update_info[key]}})
