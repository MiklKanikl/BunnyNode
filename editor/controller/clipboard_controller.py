from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from editor.items.image import ImageNode
from editor.items.node import NodeItem
from editor.items.rectangle import NodeRect
from editor.items.ellipse import NodeEllipse
from editor.items.edge import EdgeItem
from editor.items.directed_edge import DirectedEdgeItem
from editor.items.triangle import NodeTriangle

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
                elif isinstance(item, NodeTriangle):
                    typ_str = "triangle"
                node = {
                    "type": typ_str,
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "width": item.width,
                    "height": item.height,
                    "color": item.colour,
                    "text_color": [
                        item.text_color.red(),
                        item.text_color.green(),
                        item.text_color.blue()
                    ],
                    "text": item.text,
                    "id": item.id,
                    "z_value": item.zValue(),
                    "custom_param": item.custom_param
                }
                self.clipboard_data["nodes"].append(node)
            elif isinstance(item, EdgeItem):
                self.clipboard_data["edges"].append({
                    "start": item.start_node.id,
                    "end": item.end_node.id,
                    "color": item.colour,
                    "text_color": [
                        item.text_color.red(),
                        item.text_color.green(),
                        item.text_color.blue()
                    ],
                    "width": item.p_width,
                    "directed": item.directed,
                    "text": item.text,
                    "z_value": item.zValue()
                })
    def paste(self):
        if not self.clipboard_data:
            return
        
        id_map = {}
        items = []
        for data in self.clipboard_data["nodes"]:
            node = None
            if data["type"] == "rect":
                node = NodeRect(
                    data["x"] + 10, data["y"] + 10,
                    data["width"], data["height"],
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data.get("text", "")
                )
                node.apply_text_color(QColor(*data.get("text_color", [0, 0, 0])))
                items.append(node)
                id_map[data.get("id", id(node))] = node
            
            elif data["type"] == "ellipse":
                node = NodeEllipse(
                    data["x"] + 10, data["y"] + 10,
                    data["width"], data["height"],
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data.get("text", "")
                )
                node.apply_text_color(QColor(*data.get("text_color", [0, 0, 0])))
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
                node.apply_text_color(QColor(*data.get("text_color", [0, 0, 0])))
                items.append(node)
                id_map[data.get("id", id(node))] = node
            elif data["type"] == "triangle":
                node = NodeTriangle(
                    data["x"] + 10, data["y"] + 10,
                    data["width"], data["height"],
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data.get("text", "")
                )
                node.apply_text_color(QColor(*data.get("text_color", [0, 0, 0])))
                items.append(node)
                id_map[data.get("id", id(node))] = node
            if node is not None:
                node.setZValue(data.get("z_value", node.zValue()))
            
        for data in self.clipboard_data["edges"]:
            start_node = id_map.get(data["start"])
            end_node = id_map.get(data["end"])
            if start_node and end_node:
                if data["directed"] == True:
                    edge = DirectedEdgeItem(
                    start_node, end_node,
                    QColor(data["color"][0], data["color"][1], data["color"][2]),
                    data["width"],
                    text=data.get("text", "")
                )
                else:
                    edge = EdgeItem(
                        start_node, end_node,
                        QColor(data["color"][0], data["color"][1], data["color"][2]),
                        data["width"],
                        text=data.get("text", "")
                    )
                edge.apply_text_color(QColor(*data.get("text_color", [0, 0, 0])))
                edge.setZValue(data.get("z_value", edge.zValue()))
                items.append(edge)
        return items