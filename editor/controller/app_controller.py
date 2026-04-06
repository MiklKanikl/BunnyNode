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
        self.undostack = QUndoStack()
        self.clipboard = ClipboardController()
    
    def add_node(self, scene, node):
        cmd = AddNodeCommand(scene, node)
        self.undostack.push(cmd)
    
    def delete_node(self, scene, itemlist):
        cmd = DeleteNodeCommand(scene, itemlist)
        self.undostack.push(cmd)
    
    def move_node(self, node, old_pos, new_pos):
        cmd = MoveNodeCommand(node, old_pos, new_pos)
        self.undostack.push(cmd)
    
    def rename_node(self, node, old_text, new_text):
        cmd = RenameNodeCommand(node, old_text, new_text)
        self.undostack.push(cmd)
    
    def change_color(self, item, old_color, new_color):
        cmd = ChangeColorCommand(item, old_color, new_color)
        self.undostack.push(cmd)
    
    def resize_node(self, node, old_width, old_height, new_width, new_height):
        cmd = ResizeNodeCommand(node, old_width, old_height, new_width, new_height)
        self.undostack.push(cmd)
    
    def resize_edge(self, edge, old_width, new_width):
        cmd = ResizeEdgeCommand(edge, old_width, new_width)
        self.undostack.push(cmd)
    
    def paste(self, scene):
        cmd = PasteCommand(scene)
        self.undostack.push(cmd)
    
    def load_image(self, node, old_width, old_height, old_img_path, new_img_path):
        cmd = LoadImageCommand(node, old_width, old_height, old_img_path, new_img_path)
        self.undostack.push(cmd)