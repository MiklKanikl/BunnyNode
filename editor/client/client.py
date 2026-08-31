import json
import asyncio
import sys
import threading
import requests
import websockets
from PyQt6.QtCore import pyqtSignal, QObject

class Client(QObject):
    MAX_MESSAGE_LENGTH = 1048576

    message_received = pyqtSignal(str)
    connection_ready = pyqtSignal(bool)
    room_joined = pyqtSignal(dict)
    scene_updated = pyqtSignal(dict)
    user_joined = pyqtSignal(dict)
    user_left = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    undo_last_command = pyqtSignal()
    
    #REST-API: test="http://192.168.0.176:5000", prod="https://bunnynode.farni.ng"
    #WebSocket: test="ws://192.168.0.176:8765", prod="wss://bunnynode.farni.ng"
    def __init__(self, server_url=f"http://{sys.argv[1]}:5000" if len(sys.argv) > 1 else "https://bunnynode.farni.ng:5000", ws_url=f"ws://{sys.argv[1]}:8765" if len(sys.argv) > 1 else "wss://bunnynode.farni.ng:8765"):
        super().__init__()
        self.server_url = server_url
        self.ws_url = ws_url
        self.room_id = None
        self.session_id = None
        self.websocket = None
        self.loop = None
        self.thread = None
        self._loop_ready = threading.Event()
        self.running = False
        self.current_version = 0
    
    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.running = True
        self._loop_ready.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self._loop_ready.wait(timeout=1.0)
    
    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._loop_ready.set()
        try:
            self.loop.run_until_complete(self._main())
        finally:
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
            self.loop = None
    
    async def _main(self):
        while self.running:
            await asyncio.sleep(0.1)
    
    def create_room(self):
        try:
            response = requests.get(f"{self.server_url}/api/create_token/", timeout=10)
            if response.ok:
                self.room_id = int(response.text.strip())
                self.session_id = None
                return self._connect_websocket()
            else:
                self.error_occurred.emit(f"Failed to create room: {response.text}")
                return False
        except Exception as e:
            self.error_occurred.emit(f"Error creating room: {str(e)}")
            return False
    
    def join_room(self, room_id):
        try:
            self.room_id = int(room_id)
        except (TypeError, ValueError):
            self.error_occurred.emit("Invalid room token")
            return False
        self.session_id = None
        if not self._connect_websocket():
            return False
        self.request_full_state()
        return True
    
    def _connect_websocket(self):
        if not self.loop or self.loop.is_closed():
            self.error_occurred.emit("Event loop not initialized")
            return False
        asyncio.run_coroutine_threadsafe(self._websocket_connect(), self.loop)
        return True
    
    async def _websocket_connect(self):
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connection_ready.emit(True)
            
            join_msg = {
                'type': 'join',
                'room': self.room_id,
                'user_info': {'name': 'PyQt6 Client'}
            }
            await self.websocket.send(json.dumps(join_msg))
            
            async for raw_msg in self.websocket:
                await self._handle_message(raw_msg)
                
        except websockets.exceptions.ConnectionClosed:
            self.websocket = None
            self.session_id = None
            self.connection_ready.emit(False)
        except Exception as e:
            self.websocket = None
            self.session_id = None
            self.connection_ready.emit(False)
            self.error_occurred.emit(str(e))
        finally:
            if self.websocket is not None:
                self.websocket = None
                self.session_id = None
                self.connection_ready.emit(False)
    
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
                await asyncio.get_running_loop().run_in_executor(None, self.request_full_state)
                
            elif msg_type == 'update_success':
                self.current_version = msg.get('new_version', self.current_version)
            
            elif msg_type == 'error':
                self.error_occurred.emit(f"ERROR: {msg.get('message', '')}")
                
            else:
                self.message_received.emit(raw_msg)
                
        except (json.JSONDecodeError, TypeError):
            self.error_occurred.emit("Received invalid message from server")
    
    def request_full_state(self):
        try:
            response = requests.get(
                f"{self.server_url}/api/get_data/",
                params={"key": self.room_id},
                timeout=10,
            )
            if response.ok:
                data = response.json()
                self.current_version = data.get('version', 0)
                if "nodes" in data and "edges" in data:
                    data["type"] = "full_state"
                    self.scene_updated.emit(data)
            else:
                self.error_occurred.emit(f"Failed to request full state: {response.text}")
        except Exception as e:
            self.error_occurred.emit(f"Error requesting full state: {str(e)}")
    
    def send_changes(self, changes):
        if self.websocket is None or self.loop is None or self.loop.is_closed():
            self.error_occurred.emit("Not connected to WebSocket")
            self.undo_last_command.emit()
            return False
        
        if self.room_id == None or self.session_id == None:
            self.error_occurred.emit("Not in a room or session")
            self.undo_last_command.emit()
            return False
        
        msg = {
            'type': 'scene_change',
            'changes': changes,
            'version': self.current_version
        }
        
        try:
            payload = json.dumps(msg)
            if len(payload.encode("utf-8")) <= Client.MAX_MESSAGE_LENGTH:
                future = asyncio.run_coroutine_threadsafe(
                    self.websocket.send(payload), self.loop
                )
                future.add_done_callback(self._send_finished)
                return True
            else:
                self.error_occurred.emit(f"Message with {len(payload.encode('utf-8'))} bytes too long. It exceeds the {self.MAX_MESSAGE_LENGTH} bytes limit.")
                self.undo_last_command.emit()
                return False
        except Exception as e:
            self.error_occurred.emit(f"Error sending changes: {str(e)}")
            self.undo_last_command.emit()
            return False

    def _send_finished(self, future):
        try:
            future.result()
        except Exception as e:
            self.error_occurred.emit(f"Error sending changes: {str(e)}")
            self.undo_last_command.emit()

    def leave_room(self):
        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(json.dumps({'type': 'leave'})),
                    self.loop
                )
            except Exception:
                pass
            if self.loop and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
            self.websocket = None
        
        self.session_id = None
        self.room_id = None
        self.current_version = 0
    
    def disconnect(self):
        self.leave_room()
        self.running = False
        if self.thread and self.thread.is_alive() and self.thread is not threading.current_thread():
            self.thread.join(timeout=1.0)