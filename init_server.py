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

class1_query = {'class_name': 'Computer Architecture', 'class_id': '89230', 'teacher': 'Prof Kaminka G', 'description': 'Development of systemic thinking, significant improvement in students abilities in systems development, and radical change in their understanding of the work of the modern computer', 'external_links': ['https://cs.biu.ac.il/staff/121', 'https://shoham.biu.ac.il/BiuCoursesViewer/CourseSylabusView.aspx?lid=720146'], 'homework_links': [], 'updates': ['No homework for the entire semester', 'Jokes'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 2, 'start': '2021-05-10T10:00:00', 'end': '2021-05-10T11:30:00', 'img_path': 'https://cs.biu.ac.il/sites/default/files/styles/4_cols_square_img/public/2019-12/%D7%A4%D7%A8%D7%95%D7%A4%27%20%D7%92%D7%9C%20%D7%A7%D7%9E%D7%99%D7%A0%D7%A7%D7%90.jpg?itok=vLgshuw_'}
class2_query = {'class_name': 'Algorithems 2', 'class_id': '89322', 'teacher': 'Prof Amihood A', 'description': 'More advanced problems in methods studied in Algorithms I. New algorithmic methods, e.g. Linear programming. Different algorithmic paradigms, e.g. on-line algorithms, approximation algorithms, streaming, distributed algorithms, and parallel algorithms. New topics, e.g. pattern matching, compression', 'external_links': ['https://cs.biu.ac.il/staff/103', 'https://u.cs.biu.ac.il/~amir/', 'https://shoham.biu.ac.il/BiuCoursesViewer/CourseSylabusView.aspx?lid=720186'], 'homework_links': ['https://drive.google.com/drive/folders/0B_dY_D5Av8zpY19UenV3bTdNejA'], 'updates': ['Whoever approves that NP=P get 5 more points to the final score'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 4, 'start': '2021-05-12T16:00:00', 'end': '2021-05-12T18:00:00', 'img_path': 'https://cs.biu.ac.il/sites/default/files/styles/4_cols_square_img/public/2019-12/%D7%90%D7%9E%D7%99%D7%A8%20%D7%A2%D7%9E%D7%99%D7%94%D7%95%D7%93.jpg?itok=s36nN1Xw'}
class3_query = {'class_name': 'Introduction to Computer Science', 'class_id': '89110', 'teacher': 'Prof Agmon N', 'description': 'Computer science Introduction. Programming in C. Basic concepts in algorithms. Basic hardware optimizations', 'external_links': ['https://cs.biu.ac.il/staff/62', 'https://u.cs.biu.ac.il/~agmon/'], 'homework_links': ['https://lemida.biu.ac.il/'], 'updates': ['Final test cancelled'], 'test_ids': [], 'participants': ['yogevm90', 'idan57'], 'day': 4, 'start': '2021-05-12T17:00:00', 'end': '2021-05-12T19:00:00', 'img_path': 'https://cs.biu.ac.il/sites/default/files/styles/4_cols_square_img/public/2019-05/noaagmon.jpg?itok=vbr0cw5s'}
yogev_pass = "yogev"
idan_pass = "idan"

password1 = bcrypt.hashpw(yogev_pass.encode(), bcrypt.gensalt())
password2 = bcrypt.hashpw(idan_pass.encode(), bcrypt.gensalt())
user1_query = {'username': 'YogevM', 'password': password1, 'id': '00001', 'name': 'Yogev', 'surname': 'Mela', 'role': 'student', 'classes': ['89230', '89322']}
user2_query = {'username': 'GalK', 'password': password2, 'id': '00002', 'name': 'Idan', 'surname': 'Cohen', 'role': 'teacher', 'classes': ['89230', '89110', '89322']}

classes_col.insert_one(class1_query)
classes_col.insert_one(class2_query)
classes_col.insert_one(class3_query)
users_col.insert_one(user1_query)
users_col.insert_one(user2_query)
