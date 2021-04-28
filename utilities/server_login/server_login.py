import requests


class ServerLogin(object):
    SERVER = r"http://127.0.0.1:5001/Login"

    @staticmethod
    def login(username, password, is_teacher=False):
        response = requests.post(ServerLogin.SERVER, json={"username": username, "password": password})

        if response.ok:
            res_json = response.json()
            res = res_json["verdict"]
            if is_teacher:
                res = res and res_json["role"] == "teacher"
            return res

        return False
