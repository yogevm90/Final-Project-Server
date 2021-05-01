import pymongo
import bcrypt

"""
Init script for new server - start new mongodb with admin user
"""
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Scholapp"]
users_col = mydb["users"]
classes_col = mydb["classes"]
users_col.remove()
classes_col.remove()

class1_query = {'name': 'math', 'class_id': '00003', 'teacher': 'idan57@gmail.com', 'description': 'math class', 'external_links': ['www.google.com', 'www.facebook.com'], 'homework_links': ['www.ynet.co.il'], 'updates': ['update 1', 'update 2'], 'test_ids': [], 'participants': ['yogevm90@gmail.com'], 'stream_paths': [{'id': '00001', 'video': '/project/upload/video/00001', 'audio': '/project/upload/audio/00001'}, {'id': '00002', 'video': '/project/upload/video/00002', 'audio': '/project/upload/audio/00002'}], 'day': 1, 'hour': '12', 'img_path': 'www.walla.co.il' }

yogev_pass = "yogev"
idan_pass = "idan"
admin_pass = "admin"
password1 = bcrypt.hashpw(yogev_pass.encode(), bcrypt.gensalt())
password2 = bcrypt.hashpw(idan_pass.encode(), bcrypt.gensalt())
password3 = bcrypt.hashpw(admin_pass.encode(), bcrypt.gensalt())
user1_query = {'username': 'yogevm90','password': password1, 'id': '00001', 'name': 'Yogev', 'surname': 'Mela', 'role': 'student', 'classes': ['00003']}
user2_query = {'username': 'idan57', 'password': password2, 'id': '00002', 'name': 'Idan', 'surname': 'Cohen', 'role': 'teacher', 'classes': []}
admin_query = {'username': 'admin', 'password': password3, 'id': '00000', 'name': 'admin', 'surname': 'admin', 'role': 'teacher', 'classes': []}

classes_col.insert_one(class1_query)
users_col.insert_one(user1_query)
users_col.insert_one(user2_query)
users_col.insert_one(admin_query)