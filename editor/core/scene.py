from PyQt6.QtWidgets import QGraphicsScene, QColorDialog, QInputDialog, QFileDialog
from PyQt6.QtGui import QColor, QCursor, QImage, QPainter
from PyQt6.QtCore import Qt, QRectF
from editor.items.node import NodeItem
from editor.items.rectangle import NodeRect
from editor.items.ellipse import NodeEllipse
from editor.items.image import ImageNode
from editor.items.edge import EdgeItem
from editor.calculations.dijkstra import shortest_path
import os

class DiagramScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 3000, 3000)
        self.current_color = QColor(0, 150, 255)  # Standardfarbe
        self.startnode = None
        self.endnode = None
        self.controller = None
    
    def set_services(self, controller):
        self.controller = controller
    
    def export_png(self, path: str):
        EXPORT_WIDTH = 3000
        EXPORT_HEIGHT = 3000

        image = QImage(
            EXPORT_WIDTH,
            EXPORT_HEIGHT,
            QImage.Format.Format_ARGB32
        )
        image.fill(Qt.GlobalColor.black)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        source_rect = QRectF(0, 0, EXPORT_WIDTH, EXPORT_HEIGHT)
        target_rect = QRectF(0, 0, EXPORT_WIDTH, EXPORT_HEIGHT)

        self.render(painter, target_rect, source_rect)

        painter.end()

        image.save(path)
    
    def add_rect(self, x, y):
        rect = NodeRect(
            x, y,
            80, 80,
            self.current_color
        )
        if self.controller:
            self.controller.add_node(self, rect)
    
    def add_ellipse(self, x, y):
        ellp = NodeEllipse(
            x, y,
            80, 80,
            self.current_color
        )
        if self.controller:
            self.controller.add_node(self, ellp)
    
    def add_image(self, x, y):
        image = ImageNode(
            x, y,
            80, 80,
            self.current_color,
        )
        if self.controller:
            self.controller.add_node(self, image)
    
    def save_file_dialog(self):
        new_text, ok = QInputDialog.getText(
            None, "Save As", "Filename (without extension):", text="diagram"
        )
        if ok and new_text.strip():
            folder = "saves"
            os.makedirs(folder, exist_ok=True)
            filename = os.path.join(folder, new_text.strip() + ".diagram")
        else:
            return
        self.save_scene(filename)
    
    def load_file_dialog(self):
        folder = "saves"
        os.makedirs(folder, exist_ok=True)

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "load",
            folder,                      
            "Diagram-files (*.diagram *.json)"
        )
        if filename:
            self.load_scene(filename)
    
    def keyPressEvent(self, event):
        #R -> neues Rechteck an Mausposition
        if event.key() == Qt.Key.Key_R:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            self.add_rect(pos.x(), pos.y())
        #E -> neuer Kreis an Mausposition
        elif event.key() == Qt.Key.Key_E:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            self.add_ellipse(pos.x(), pos.y())
        #1 -> Farbe ändern
        elif event.key() == Qt.Key.Key_1:
            chosen = QColorDialog.getColor(self.current_color)
            if chosen.isValid():
                self.current_color = chosen
            return
        #L -> Kante zwischen zwei ausgewählten Nodes erstellen
        elif event.key() == Qt.Key.Key_L:
            selected = [i for i in self.selectedItems() if isinstance(i, NodeItem)]
            if len(selected) == 2:
                edge = EdgeItem(selected[0], selected[1])
                if self.controller:
                    self.controller.add_node(self, edge)
                return
        #Entf -> ausgewählte Items löschen
        elif event.key() == Qt.Key.Key_Delete:
            self.delete()
            return
        # Ctrl+S -> Szene speichern
        elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.save_file_dialog()
            return
        # Ctrl+O -> Szene laden
        elif event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.load_file_dialog()
            return
        # Crtl+C -> Kopieren
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.clipboard.copy(self.selectedItems())
            return
        # Ctrl+V -> Einfügen
        elif event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.paste(self)
            return
        # Ctrl+X -> Ausschneiden
        elif event.key() == Qt.Key.Key_X and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.clipboard.copy(self.selectedItems())
            self.delete()
            return
        # Ctrl+D -> Duplizieren
        elif event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.controller.clipboard.copy(self.selectedItems())
            self.controller.paste(self)
            return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        self.old_pos_list = []
        self.itemlist = []
        for i in self.items():
            if isinstance(i, NodeItem):
                self.old_pos_list.append(i.pos())
                self.itemlist.append(i)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        new_pos_list = []
        for i in self.items():
            if isinstance(i, NodeItem):
                new_pos_list.append(i.pos())
        if self.items() != []:
            for i in self.old_pos_list:
                if i != new_pos_list[self.old_pos_list.index(i)]:
                    self.controller.move_node(self.itemlist, self.old_pos_list, new_pos_list)
                    break
    
    def delete(self):
        itemlist = []
        for item in self.selectedItems():
            if isinstance(item, NodeItem):
                for edge in item.edges[:]:
                    itemlist.append(edge)
                itemlist.append(item)
            elif isinstance(item, EdgeItem):
                itemlist.append(item)
        self.controller.delete_node(self, itemlist)

    def save_scene(self, filename): # Szene speichern
        data = {
            "nodes": [],
            "edges": []
        }
        for item in self.items():
            if isinstance(item, NodeItem):
                typ_str = ""
                if isinstance(item, NodeRect):
                    typ_str = "rect"
                elif isinstance(item, NodeEllipse):
                    typ_str = "ellipse"
                elif isinstance(item, ImageNode):
                    typ_str = "image"
                node = {
                    "id": item.id,
                    "type": typ_str,
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "width": item.width,
                    "height": item.height,
                    "color": item.colour,
                    "text": item.text,
                    "custom_param": item.custom_param
                }
                data["nodes"].append(node)

            elif isinstance(item, EdgeItem): # Edges
                data["edges"].append({
                    "start": item.start_node.id,
                    "end": item.end_node.id,
                    "color": item.colour,
                    "width": item.p_width
                })
        import json
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def load_scene(self, filename): # Datei laden
        import json
        with open(filename, "r") as f:
            data = json.load(f)

        self.clear()
        id_map = {}

        # Nodes
        for n in data["nodes"]:
            if n["type"] == "rect":
                node = NodeRect(
                    n["x"], n["y"],
                    n["width"], n["height"],
                    QColor(n["color"][0], n["color"][1], n["color"][2]),
                    text=n.get("text", "")
                )
            elif n["type"] == "ellipse":
                node = NodeEllipse(
                    n["x"], n["y"],
                    n["width"], n["height"],
                    QColor(n["color"][0], n["color"][1], n["color"][2]),
                    text=n.get("text", "")
                )
            elif n["type"] == "image":
                node = ImageNode(
                    n["x"], n["y"],
                    n["width"], n["height"],
                    QColor(n["color"][0], n["color"][1], n["color"][2]),
                    custom_param=n.get("custom_param", [])
                )
            node.id = n["id"]
            id_map[node.id] = node
            if self.controller:
                self.controller.add_node(self, node)

        # Edges
        for e in data["edges"]:
            start = id_map[e["start"]]
            end = id_map[e["end"]]
            color = QColor(e["color"][0], e["color"][1], e["color"][2])
            width = e["width"]
            edge = EdgeItem(start, end, color, width)
            if self.controller:
                self.controller.add_node(self, edge)
    
    def weighted_graph(self): # Graph mit Kantenlängen (gewichtet)
        g = {}
        for i in self.items():
            if isinstance(i, NodeRect) or isinstance(i, NodeEllipse):
                g[i] = []
            elif isinstance(i, EdgeItem):
                dist = i.laenge()
                g[i.start_node].append((i.end_node, dist))
                g[i.end_node].append((i.start_node, dist))
        return g
    
    def show_distance(self, text):
        for v in self.views():
            win = v.window()
            if hasattr(win, "status"):
                win.status.setText(text)
    
    def compute_shortest(self, a, b):
        g = self.weighted_graph()
        d, prev = shortest_path(g, a, b)
        if d is None:
            self.show_distance("No path found")
        else:
            self.show_distance(f"Distance: {round(d,2)}")

    def setup_path_compution(self):
        if self.startnode and self.endnode and self.startnode in self.items() and self.endnode in self.items():
            self.compute_shortest(self.startnode, self.endnode)
        else:
            self.show_distance("No nodes selected")