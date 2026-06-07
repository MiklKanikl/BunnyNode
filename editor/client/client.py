from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QTimer
import requests

class Client(QObject):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.timer = QTimer()
        self.timer.timeout.connect(self.periodic_pull)
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        self.current_version = 0
        self.server_url = "http://192.168.0.176:5000"
        self.pending_changes = False
    
    def mark_changes(self):
        self.pending_changes = True
    
    def periodic_pull(self):
        try:
            data = self.pull_scene(self.win.token)
            if data:
                server_version = data.get("version", 0)
                if server_version > self.current_version:
                    self.current_version = server_version
                    scene_data = {
                        "nodes": data.get("nodes", []),
                        "edges": data.get("edges", [])
                    }
                    self.win.view.scene().load_scene(online=True, data=scene_data)
        except Exception as e:
            print(f"Periodic pull error: {str(e)}")
            pass

    def start_timer(self, intervall=1000):
        self.timer.start(intervall)
        self.sync_timer.start(2000)

    def stop_timer(self):
        self.timer.stop()
        self.sync_timer.stop()
    
    def auto_sync(self):
        """Automatically sync pending changes to server"""
        if self.pending_changes and self.win.online:
            try:
                scene_data = self.win.view.scene().save_scene(online=True)
                if scene_data:
                    self.commit_scene(self.win.token, scene_data)
                    self.pending_changes = False
            except Exception as e:
                print(f"Auto-sync error: {str(e)}")

    def create_token(self):
        try:
            response = requests.get(f"{self.server_url}/api/create_token/")
            if response.status_code == 200:
                token = int(response.text)
                self.current_version = 0
                return token
            else:
                raise ConnectionError("Connection to API failed")
        except Exception as e:
            raise ConnectionError(f"Failed to create token: {str(e)}")

    def commit_scene(self, key, data):
        try:
            response = requests.post(
                f"{self.server_url}/api/send_data/",
                json={"key": key, "data": data}
            )
            if response.status_code == 200:
                server_data = self.pull_scene(key)
                self.current_version = server_data.get("version", 0)
            else:
                raise ConnectionError(f"Server error: {response.text}")
        except Exception as e:
            raise ConnectionError(f"Failed to commit scene: {str(e)}")
    
    def send_delta(self, key, changes, base_version):
        try:
            response = requests.post(
                f"{self.server_url}/api/send_delta/",
                json={
                    "key": key,
                    "base_version": base_version,
                    "changes": changes
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                self.current_version = result.get("new_version", 0)
                return True
            elif response.status_code == 409:
                result = response.json()
                raise ConnectionError(f"Version conflict. Server version: {result.get('server_version')}")
            else:
                raise ConnectionError(f"Server error: {response.text}")
        except Exception as e:
            raise ConnectionError(f"Failed to send delta: {str(e)}")
    
    def pull_scene(self, key):
        try:
            response = requests.get(
                f"{self.server_url}/api/get_data/",
                params={"key": key}
            )
            if response.status_code == 200:
                data = response.json()
                self.current_version = data.get("version", 0)
                return data
            else:
                raise ConnectionError(f"Server error: {response.text}")
        except Exception as e:
            raise ConnectionError(f"Failed to pull scene: {str(e)}")