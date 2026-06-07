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
from editor.path_utils import get_settings_path

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
        import os
        settings_path = get_settings_path()
        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}
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
                self.win.client.pending_changes = True
            except Exception as e:
                print(f"Sync error: {str(e)}")
        else:
            self.undostack.push(cmd)