from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, QTimer
import requests
import json

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
        self.last_synced_state = None  # Track last state we sent to server
        self.pending_changes = False
    
    def periodic_pull(self):
        """Pull changes from server every 3 seconds"""
        try:
            data = self.pull_scene(self.win.token)
            if data:
                server_version = data.get("version", 0)
                # Check if server state is different from our last known state
                current_state = json.dumps({
                    "nodes": data.get("nodes", []),
                    "edges": data.get("edges", [])
                }, sort_keys=True)
                
                # Only reload if content actually changed
                if current_state != self.last_synced_state:
                    self.current_version = server_version
                    self.last_synced_state = current_state
                    scene_data = {
                        "nodes": data.get("nodes", []),
                        "edges": data.get("edges", [])
                    }
                    self.win.view.scene().load_scene(online=True, data=scene_data)
        except Exception as e:
            print(f"Periodic pull error: {str(e)}")

    def start_timer(self, intervall=1000):
        self.timer.start(3000)  # Pull every 3 seconds instead of 1
        self.sync_timer.start(intervall)  # Use provided interval for sync (default 1000)

    def stop_timer(self):
        self.timer.stop()
        self.sync_timer.stop()
    
    def auto_sync(self):
        """Automatically sync pending changes to server every 1 second"""
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
                self.last_synced_state = None
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
                self.current_version += 1
                self.last_synced_state = json.dumps({
                    "nodes": data.get("nodes", []),
                    "edges": data.get("edges", [])
                }, sort_keys=True)
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