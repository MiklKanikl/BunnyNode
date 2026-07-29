import json
import asyncio
import threading
import requests
import websockets
from PyQt6.QtCore import pyqtSignal, QObject

class Client(QObject):
    message_received = pyqtSignal(str)
    connection_ready = pyqtSignal(bool)
    room_joined = pyqtSignal(dict)
    scene_updated = pyqtSignal(dict)
    user_joined = pyqtSignal(dict)
    user_left = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    #REST-API: test="http://192.168.0.176:5000", prod="http://bunnynode.farni.ng"
    #WebSocket: test="ws://192.168.0.176:5000", prod="wss://bunnynode.farni.ng"
    def __init__(self, server_url="http://192.168.0.176:5000", ws_url="ws://192.168.0.176:8765"):
        super().__init__()
        self.server_url = server_url
        self.ws_url = ws_url
        self.room_id = None
        self.session_id = None
        self.websocket = None
        self.loop = None
        self.thread = None
        self.running = False
        self.current_version = 0
    
    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._main())
    
    async def _main(self):
        self.connection_ready.emit(True)
        while self.running:
            await asyncio.sleep(0.1)
    
    def create_room(self):
        try:
            response = requests.get(f"{self.server_url}/api/create_token/")
            if response.ok:
                self.room_id = int(response.text)
                self._connect_websocket()
                return True
            else:
                self.error_occurred.emit(f"Failed to create room: {response.text}")
                return False
        except Exception as e:
            self.error_occurred.emit(f"Error creating room: {str(e)}")
            return False
    
    def join_room(self, room_id):
        self.room_id = room_id
        self._connect_websocket()
        self.request_full_state()
    
    def _connect_websocket(self):
        if not self.loop:
            self.error_occurred.emit("Event loop not initialized")
            return
        asyncio.run_coroutine_threadsafe(self._websocket_connect(), self.loop)
    
    async def _websocket_connect(self):
        try:
            self.websocket = await websockets.connect(self.ws_url)
            
            join_msg = {
                'type': 'join',
                'room': self.room_id,
                'user_info': {'name': 'PyQt6 Client'}
            }
            await self.websocket.send(json.dumps(join_msg))
            
            async for raw_msg in self.websocket:
                await self._handle_message(raw_msg)
                
        except websockets.exceptions.ConnectionClosed as e:
            self.connection_ready.emit(False)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    async def _handle_message(self, raw_msg):
        try:
            msg = json.loads(raw_msg)
            msg_type = msg.get('type')
            
            if msg_type == 'joined':
                self.session_id = msg.get('session_id')
                self.current_version = msg.get('version', 0)
                self.room_joined.emit(msg)
                
            elif msg_type == 'scene_update':
                self.current_version = msg.get('version', self.current_version)
                self.scene_updated.emit(msg)
                
            elif msg_type == 'user_joined':
                self.user_joined.emit(msg)
                
            elif msg_type == 'user_left':
                self.user_left.emit(msg)
                
            elif msg_type == 'conflict':
                self.request_full_state()
                
            elif msg_type == 'update_success':
                self.current_version = msg.get('new_version', self.current_version)
            
            elif msg_type == 'error':
                self.error_occurred.emit(f"ERROR: {msg.get('message', "")}")
                
            else:
                self.message_received.emit(raw_msg)
                
        except json.JSONDecodeError:
            pass
    
    def request_full_state(self):
        try:
            response = requests.get(
                f"{self.server_url}/api/get_data/",
                params={"key": self.room_id}
            )
            if response.ok:
                data = response.json()
                self.current_version = data.get('version', 0)
        except Exception as e:
            self.error_occurred.emit(f"Error requesting full state: {str(e)}")
    
    def send_changes(self, changes):
        if self.websocket == None:
            self.error_occurred.emit("Not connected to WebSocket")
            return False
        
        if self.room_id == None or self.session_id == None:
            self.error_occurred.emit("Not in a room or session")
            return False
        
        msg = {
            'type': 'scene_change',
            'changes': changes,
            'version': self.current_version
        }
        
        try:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(msg)),
                self.loop
            )
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error sending changes: {str(e)}")
            return False
    
    def leave_room(self):
        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(json.dumps({'type': 'leave'})),
                    self.loop
                )
            except:
                pass
            asyncio.run_coroutine_threadsafe(
                self.websocket.close(),
                self.loop
            )
            self.websocket = None
        
        self.session_id = None
        self.room_id = None
        self.current_version = 0
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
    
    def disconnect(self):
        self.leave_room()