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
from editor.items.node import NodeItem
from editor.items.edge import EdgeItem
from editor.path_utils import get_settings_path

class AppController:
    def __init__(self):
        self.scene = None
        self.undostack = QUndoStack()
        self.clipboard = ClipboardController()
        self.changes = {}
    
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
    
    def add_node(self, scene, item):
        cmd = AddNodeCommand(scene, item)
        self.changes = {}
        ch_type = ''
        if isinstance(item, NodeItem):
            ch_type = 'nodes_added'
            self.changes['nodes'] = [item.to_dict()]
        elif isinstance(item, EdgeItem):
            ch_type = 'edges_added'
            self.changes['edges'] = [item.to_dict()]
        self.changes['type'] = ch_type
        self.push_command(cmd)
    
    def delete_node(self, scene, itemlist):
        cmd = DeleteNodeCommand(scene, itemlist)
        self.changes = {
            'type': 'nodes_and_edges_removed',
            'nodes': [item.to_dict() for item in itemlist if isinstance(item, NodeItem)],
            'edges': [item.to_dict() for item in itemlist if isinstance(item, EdgeItem)]
        }
        self.push_command(cmd)
    
    def move_node(self, nodelist, old_pos, new_pos):
        cmd = MoveNodeCommand(nodelist, old_pos, new_pos)
        self.changes = {
            'type': 'nodes_modified',
            'nodes': [node.to_dict() for node in nodelist]
        }
        self.push_command(cmd)
    
    def rename_node(self, node, old_text, new_text):
        cmd = RenameNodeCommand(node, old_text, new_text)
        nodedata = node.to_dict()
        nodedata["text"] = new_text
        self.changes = {
            'type': 'nodes_modified',
            'nodes': [nodedata]
        }
        self.push_command(cmd)
    
    def change_color(self, item, old_color, new_color):
        cmd = ChangeColorCommand(item, old_color, new_color)
        itemdata = item.to_dict()
        itemdata["color"] = [new_color.red(), new_color.green(), new_color.blue()]
        if isinstance(item, NodeItem):
            self.changes = {
                'type': 'nodes_modified',
                'nodes': [itemdata]
            }
        elif isinstance(item, EdgeItem):
            self.changes = {
                'type': 'edges_modified',
                'edges': [itemdata]
            }
        self.push_command(cmd)
    
    def resize_node(self, node, old_width, old_height, new_width, new_height):
        cmd = ResizeNodeCommand(node, old_width, old_height, new_width, new_height)
        nodedata = node.to_dict()
        nodedata["width"] = new_width
        nodedata["height"] = new_height
        self.changes = {
            'type': 'nodes_modified',
            'nodes': [nodedata]
        }
        self.push_command(cmd)
    
    def resize_edge(self, edge, old_width, new_width):
        cmd = ResizeEdgeCommand(edge, old_width, new_width)
        edgedata = edge.to_dict()
        edgedata["width"] = new_width
        self.changes = {
            'type': 'edges_modified',
            'edges': [edgedata]
        }
        self.push_command(cmd)
    
    def paste(self, scene):
        cmd = PasteCommand(scene)
        self.changes = {
            'type': 'nodes_and_edges_added',
            'nodes': [item.to_dict() for item in cmd.added_items if isinstance(item, NodeItem)],
            'edges': [item.to_dict() for item in cmd.added_items if isinstance(item, EdgeItem)]
        }
        self.push_command(cmd)
    
    def load_image(self, node, old_width, old_height, old_img_path, new_img_path):
        cmd = LoadImageCommand(node, old_width, old_height, old_img_path, new_img_path)
        nodedata = node.to_dict()
        nodedata["custom_param"][0] = new_img_path
        self.changes = {
            'type': 'nodes_modified',
            'nodes': [nodedata]
        }
        self.push_command(cmd)

    def undo_action(self):
        if not self.win.online:
            self.undostack.undo()

    def redo_action(self):
        if not self.win.online:
            self.undostack.redo()
    
    def clear_history(self):
        self.undostack.clear()
    
    def push_command(self, cmd):
        if self.win.online:
            try:
                self.undostack.push(cmd)
                self.win.client.send_changes(self.changes)
            except Exception as e:
                print(f"Sync error: {str(e)}")
        else:
            self.undostack.push(cmd)