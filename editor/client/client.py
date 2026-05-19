from PyQt6.QtCore import QObject
import requests

class Client(QObject):
    def create_token(self):
        request = requests.get("http://127.0.0.1:5000/api/create_token")
        if request.status_code == 200:
            return request.text
        else:
            raise ConnectionError("Connection to API failed")

    def commit_scene(self, key, data):
        request = requests.post("http://127.0.0.1:5000/api/send_data", json={"key": key, "data": data})
        if request.status_code != 200:
            raise ConnectionError("Connection to API failed")
        
    def pull_scene(self, key):
        request = requests.post("http://127.0.0.1:5000/api/get_data", params={"key": key})
        if request.status_code == 200:
            data = request.json()
        else:
            raise ConnectionError("Connection to API failed")

        return data