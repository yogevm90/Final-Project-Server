import pymongo

from Server.database_manager.authentication_manager.authentication_manager import AuthenticationManager
from Server.database_manager.data_manager.database_data_manager import DatabaseDataManager


def database_manager():
    database_client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = database_client['test']
    users_collection = database["users"]
    classes_collection = database["classes"]
    users_collection.remove()
    classes_collection.remove()
    add_user_query = {'username': 'dani', 'password': '1234', 'details': {'age': 3}}
    add_user_query1 = {'username': 'moshe', 'password': '1234', 'details': {'age': 3}}
    add_user_query2 = {'username': 'teacher', 'password': '1234', 'details': {'age': 27}}
    add_user_query3 = {'username': 'lily', 'password': '1234', 'details': {'age': 4}}
    add_user_query4 = {'username': 'lola', 'password': '1234', 'details': {'age': 5}}
    add_class_query = {'name': 'class1', 'teacher': 'dana'}
    add_class_query1 = {'name': 'class2', 'teacher': 'moshiko', 'participants': ['lily', 'lola'],
                        'details': {'date': '230321'}}
    hashed_password = AuthenticationManager.get_hashed_password('password')
    add_user_query5 = {'username': 'yoni', 'password': hashed_password, 'details': {'age': 3}}
    add_user_query6 = {'username': 'haim', 'password': hashed_password, 'details': {'age': 3}, 'admin': 'True'}
    users_collection.insert_one(add_user_query)
    users_collection.insert_one(add_user_query1)
    users_collection.insert_one(add_user_query2)
    users_collection.insert_one(add_user_query3)
    users_collection.insert_one(add_user_query4)
    users_collection.insert_one(add_user_query5)
    users_collection.insert_one(add_user_query6)
    classes_collection.insert_one(add_class_query)
    classes_collection.insert_one(add_class_query1)
    return DatabaseDataManager('test')