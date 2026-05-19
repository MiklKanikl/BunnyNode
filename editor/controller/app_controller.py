from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QUndoStack
from editor.commands.add_node import AddNodeCommand
from editor.commands.delete_node import DeleteNodeCommand
from editor.commands.load_image_command import LoadImageCommand
from editor.commands.move_node import MoveNodeCommand
from editor.commands.rename_node import RenameNodeCommand
from editor.commands.change_color import ChangeColorCommand
from editor.commands.resize_node import ResizeNodeCommand
from editor.commands.resize_edge import ResizeEdgeCommand
from editor.commands.paste_command import PasteCommand
from editor.controller.clipboard_controller import ClipboardController

class AppController:
    def __init__(self):
        self.scene = None
        self.undostack = QUndoStack()
        self.clipboard = ClipboardController()
    
    def set_scene(self, scene):
        self.scene = scene
        self.win = self.scene.views()[0].window()
    
    def get_current_settings(self):
        import json
        with open("your_settings.json", "r") as f:
            settings = json.load(f)
        return settings
    
    def add_node(self, scene, node):
        cmd = AddNodeCommand(scene, node)
        self.push_command(cmd)
    
    def delete_node(self, scene, itemlist):
        cmd = DeleteNodeCommand(scene, itemlist)
        self.push_command(cmd)
    
    def move_node(self, node, old_pos, new_pos):
        cmd = MoveNodeCommand(node, old_pos, new_pos)
        self.push_command(cmd)
    
    def rename_node(self, node, old_text, new_text):
        cmd = RenameNodeCommand(node, old_text, new_text)
        self.push_command(cmd)
    
    def change_color(self, item, old_color, new_color):
        cmd = ChangeColorCommand(item, old_color, new_color)
        self.push_command(cmd)
    
    def resize_node(self, node, old_width, old_height, new_width, new_height):
        cmd = ResizeNodeCommand(node, old_width, old_height, new_width, new_height)
        self.push_command(cmd)
    
    def resize_edge(self, edge, old_width, new_width):
        cmd = ResizeEdgeCommand(edge, old_width, new_width)
        self.push_command(cmd)
    
    def paste(self, scene):
        cmd = PasteCommand(scene)
        self.push_command(cmd)
    
    def load_image(self, node, old_width, old_height, old_img_path, new_img_path):
        cmd = LoadImageCommand(node, old_width, old_height, old_img_path, new_img_path)
        self.push_command(cmd)
    
    def clear_history(self):
        self.undostack.clear()
    
    def push_command(self, cmd):
        if self.win.online:
            try:
                self.undostack.push(cmd)
                data =self.scene.save_scene(online=True)
                self.win.client.commit_scene(self.win.token, data)
            except Exception as e:
                QMessageBox.critical(self.win, "Error", f"Failed to sync with server: {str(e)}")
                self.clear_history()
                self.scene.clear()
        else:
            self.undostack.push(cmd)