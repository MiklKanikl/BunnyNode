from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QTimer
import requests

class Client(QObject):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.timer = QTimer()
        self.timer.timeout.connect(self.periodic_pull)
    
    def periodic_pull(self):
        try:
            data = self.pull_scene(self.win.token)
            self.win.view.scene().load_scene(online=True, data=data)
        except Exception as e:
            self.win.back_to_welcome()
            QMessageBox.critical(self.win, "Error", f"Failed to sync with server: {str(e)}")

    def start_timer(self, intervall=1500):
        self.timer.start(intervall)

    def stop_timer(self):
        self.timer.stop()

    def create_token(self):
        request = requests.get("http://192.168.0.176:5000/api/create_token")
        if request.status_code == 200:
            return request.text
        else:
            raise ConnectionError("Connection to API failed")

    def commit_scene(self, key, data):
        request = requests.post("http://192.168.0.176:5000/api/send_data", json={"key": key, "data": data})
        if request.status_code != 200:
            raise ConnectionError("Connection to API failed")
        
    def pull_scene(self, key):
        request = requests.post("http://192.168.0.176:5000/api/get_data", params={"key": key})
        if request.status_code == 200:
            data = request.json()
        else:
            raise ConnectionError("Connection to API failed")

        return data