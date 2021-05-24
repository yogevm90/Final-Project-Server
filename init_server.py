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

class1_query = {'class_name': 'math', 'class_id': '00003', 'teacher': 'admin', 'description': 'math class', 'external_links': ['www.google.com', 'www.facebook.com'], 'homework_links': ['www.ynet.co.il'], 'updates': ['update 1', 'update 2'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 2, 'start': '2021-05-10T10:00:00', 'end': '2021-05-10T11:00:00', 'img_path': 'https://i.imgur.com/wy3M2bY.jpeg'}
class2_query = {'class_name': 'physics', 'class_id': '00004', 'teacher': 'admin', 'description': 'its a nice good class', 'external_links': ['www.wiki.com', 'www.facebook.com'], 'homework_links': ['www.ynet.co.il'], 'updates': ['update 1', 'update 2'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 4, 'start': '2021-05-12T16:00:00', 'end': '2021-05-12T18:00:00', 'img_path': 'https://i.imgur.com/UJ6LIOh.jpeg'}
class3_query = {'class_name': 'google', 'class_id': '00005', 'teacher': 'admin', 'description': 'google searching all day long', 'external_links': ['www.google.com', 'www.facebook.com'], 'homework_links': ['www.ynet.co.il'], 'updates': ['update 1', 'update 2'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 4, 'start': '2021-05-12T17:00:00', 'end': '2021-05-12T19:00:00', 'img_path': 'https://i.imgur.com/46DYgv1.jpeg'}
class4_query = {'class_name': 'tanah', 'class_id': '00006', 'teacher': 'admin', 'description': 'bible class', 'external_links': ['www.google.com', 'www.facebook.com'], 'homework_links': ['www.ynet.co.il'], 'updates': ['update 1', 'update 2'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 3, 'start': '2021-05-11T10:00:00', 'end': '2021-05-11T11:00:00', 'img_path': 'https://i.imgur.com/4ixmwP1.jpeg'}
yogev_pass = "yogev"
idan_pass = "idan"
admin_pass = "admin"
password1 = bcrypt.hashpw(yogev_pass.encode(), bcrypt.gensalt())
password2 = bcrypt.hashpw(idan_pass.encode(), bcrypt.gensalt())
password3 = bcrypt.hashpw(admin_pass.encode(), bcrypt.gensalt())
user1_query = {'username': 'yogevm90', 'password': password1, 'id': '00001', 'name': 'Yogev', 'surname': 'Mela', 'role': 'student', 'classes': ['00003', '00004']}
user2_query = {'username': 'idan57', 'password': password2, 'id': '00002', 'name': 'Idan', 'surname': 'Cohen', 'role': 'teacher', 'classes': ['00003', '00005', '00004']}
admin_query = {'username': 'admin', 'password': password3, 'id': '00000', 'name': 'admin', 'surname': 'admin', 'role': 'teacher', 'classes': []}

classes_col.insert_one(class1_query)
classes_col.insert_one(class2_query)
classes_col.insert_one(class3_query)
classes_col.insert_one(class4_query)
users_col.insert_one(user1_query)
users_col.insert_one(user2_query)
users_col.insert_one(admin_query)
