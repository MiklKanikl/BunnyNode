from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from editor.items.image import ImageNode
from editor.items.node import NodeItem
from editor.items.rectangle import NodeRect
from editor.items.ellipse import NodeEllipse
from editor.items.edge import EdgeItem

class ClipboardController:
    def __init__(self):
        self.clipboard_data = None
    
    def copy(self, items):
        self.clipboard_data = {
            "nodes": [],
            "edges": []
        }
        for item in items:
            if isinstance(item, NodeItem):
                typ_str = ""
                if isinstance(item, NodeRect):
                    typ_str = "rect"
                elif isinstance(item, NodeEllipse):
                    typ_str = "ellipse"
                elif isinstance(item, ImageNode):
                    typ_str = "image"
                node = {
                    "type": typ_str,
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "width": item.width,
                    "height": item.height,
                    "color": item.colour,
                    "text": item.text,
                    "id": item.id,
                    "custom_param": item.custom_param
                }
                self.clipboard_data["nodes"].append(node)
            elif isinstance(item, EdgeItem):
                self.clipboard_data["edges"].append({
                    "start": item.start_node.id,
                    "end": item.end_node.id,
                    "color": item.colour,
                    "width": item.p_width
                })
    def paste(self):
        if not self.clipboard_data:
            return
        
        id_map = {}
        items = []
        for data in self.clipboard_data["nodes"]:
            if data["type"] == "rect":
                node = NodeRect(
                    data["x"] + 10, data["y"] + 10,
                    data["width"], data["height"],
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data.get("text", "")
                )
                items.append(node)
                id_map[data.get("id", id(node))] = node
            
            elif data["type"] == "ellipse":
                node = NodeEllipse(
                    data["x"] + 10, data["y"] + 10,
                    data["width"], data["height"],
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data.get("text", "")
                )
                items.append(node)
                id_map[data.get("id", id(node))] = node
            elif data["type"] == "image":
                node = ImageNode(
                    data["x"] + 10, data["y"] + 10,
                    data["width"], data["height"],
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    text=data.get("text", ""),
                    custom_param=data.get("custom_param", [])
                )
                items.append(node)
                id_map[data.get("id", id(node))] = node
            
        for data in self.clipboard_data["edges"]:
            start_node = id_map.get(data["start"])
            end_node = id_map.get(data["end"])
            if start_node and end_node:
                edge = EdgeItem(
                    start_node, end_node,
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data["width"]
                )
                items.append(edge)
        return items