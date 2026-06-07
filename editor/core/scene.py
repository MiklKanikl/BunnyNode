from PyQt6.QtWidgets import QGraphicsScene, QColorDialog, QInputDialog, QFileDialog, QMessageBox, QGraphicsPixmapItem
from PyQt6.QtGui import QBrush, QColor, QCursor, QImage, QPainter, QTransform
from PyQt6.QtCore import Qt, QRectF
from editor.items.node import NodeItem
from editor.items.rectangle import NodeRect
from editor.items.ellipse import NodeEllipse
from editor.items.image import ImageNode
from editor.items.edge import EdgeItem
from editor.items.directed_edge import DirectedEdgeItem
from editor.calculations.dijkstra import shortest_path
from editor.path_utils import get_saves_directory
import os

class DiagramScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 3000, 3000)
        self.current_color = QColor(0, 150, 255)
        self.current_color_edge = QColor(0, 0, 0)
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.startnode = None
        self.endnode = None
        self.edge_nodes = [None, None]
        self.controller = None
        self.creating_edge = 0
        self.win = None
        self.directed_edge_mode = False
    
    def set_services(self, controller):
        self.controller = controller
        self.controller.set_scene(self)
        self.win = self.views()[0].window()
    
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
            folder = get_saves_directory()
            filename = os.path.join(folder, new_text.strip() + ".diagram")
        else:
            return
        self.save_scene(filename)
        self.update_recent_files(filename)
    
    def load_file_dialog(self):
        folder = get_saves_directory()

        filename, _ = QFileDialog.getOpenFileName(
            None,
            "load",
            folder,                      
            "Diagram-files (*.diagram *.json)"
        )
        if filename:
            self.load_scene(filename)
            self.update_recent_files(filename)
    
    def load_popup(self):
        popup = QMessageBox()
        popup.setWindowTitle("Warning")
        popup.setText("Do you want to load a new diagram? All unsaved changes will be lost.")
        popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if popup.exec() == QMessageBox.StandardButton.Yes:
            self.load_file_dialog()
    
    def color_dialog(self, item_type):
        if item_type == 0:
            new_color = QColorDialog.getColor(self.current_color)
            if new_color.isValid():
                self.current_color = new_color
        else:
            new_color = QColorDialog.getColor(self.current_color_edge)
            if new_color.isValid():
                self.current_color_edge = new_color
    
    def edge_create_dialog(self, directed):
        if self.creating_edge == 0:
                self.win.status.setText("Select first node")
                self.creating_edge = 1
                self.directed_edge_mode = directed
    
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
            self.color_dialog(0)
            return
        #2 -> Farbe der Kante ändern
        elif event.key() == Qt.Key.Key_2:
            self.color_dialog(1)
            return
        # I -> neues Bild an Mausposition
        elif event.key() == Qt.Key.Key_I:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            self.add_image(pos.x(), pos.y())
            return
        # Shift + L -> gerichtete Kante zwischen zwei ausgewählten Nodes erstellen
        elif event.key() == Qt.Key.Key_L and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.edge_create_dialog(True)
            return
        #L -> Kante zwischen zwei ausgewählten Nodes erstellen
        elif event.key() == Qt.Key.Key_L:
            self.edge_create_dialog(False)
            return
        
        # Esc -> Auswahl aufheben
        elif event.key() == Qt.Key.Key_Escape:
            self.creating_edge = 0
            self.edge_nodes = [None, None]
            self.win.status.setText("idle")
            self.clearSelection()
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
            self.load_popup()
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
        if self.creating_edge == 1:
            self.edge_nodes[0] = self.itemAt(event.scenePos(), QTransform())
            if self.edge_nodes[0] and (isinstance(self.edge_nodes[0], NodeItem) or isinstance(self.edge_nodes[0].parentItem(), NodeItem)):
                self.win.status.setText("Select second node")
                self.creating_edge = 2
        elif self.creating_edge == 2:
            self.edge_nodes[1] = self.itemAt(event.scenePos(), QTransform())
            if self.edge_nodes[1] and (isinstance(self.edge_nodes[1], NodeItem) or isinstance(self.edge_nodes[1].parentItem(), NodeItem)) and self.edge_nodes[0] != self.edge_nodes[1]:
                if not isinstance(self.edge_nodes[0], NodeItem):
                    self.edge_nodes[0] = self.edge_nodes[0].parentItem()
                if not isinstance(self.edge_nodes[1], NodeItem):
                    self.edge_nodes[1] = self.edge_nodes[1].parentItem()
                if self.directed_edge_mode:
                    edge = DirectedEdgeItem(self.edge_nodes[0], self.edge_nodes[1], self.current_color_edge)
                else:
                    edge = EdgeItem(self.edge_nodes[0], self.edge_nodes[1], self.current_color_edge)
                self.controller.add_node(self, edge)
            self.directed_edge_mode = False
            self.creating_edge = 0
            self.edge_nodes = [None, None]
            self.win.status.setText("idle")
    
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

    def save_scene(self, online=False, filename=""):
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

            elif isinstance(item, EdgeItem):
                data["edges"].append({
                    "start": item.start_node.id,
                    "end": item.end_node.id,
                    "color": item.colour,
                    "width": item.p_width,
                    "directed": item.directed
                })
        import json
        if online:
            return data
        else:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
    
    def load_scene(self, online=False, filename="", data={}):
        import json
        if not online:
            with open(filename, "r") as f:
                data = json.load(f)

        self.clear()
        id_map = {}

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

        for e in data["edges"]:
            start = id_map[e["start"]]
            end = id_map[e["end"]]
            color = QColor(e["color"][0], e["color"][1], e["color"][2])
            width = e["width"]
            if e["directed"] == True:
                edge = DirectedEdgeItem(start, end, color, width)
            else:
                edge = EdgeItem(start, end, color, width)
            if self.controller:
                self.controller.add_node(self, edge)
    
    def update_recent_files(self, filename):
        import json
        from editor.path_utils import get_data_directory, get_application_path
        
        if hasattr(self, 'win') and self.win:
            app_path = get_application_path()
        else:
            app_path = get_application_path()
        recent_files_path = os.path.join(app_path, "editor", "recent_files.json")
        
        try:
            with open(recent_files_path, "r") as f:
                recent_files = json.load(f)
        except FileNotFoundError:
            recent_files = []
        
        last_folder = os.path.basename(os.path.dirname(filename))
        fname = os.path.basename(filename)
        folder_name = os.path.join(last_folder, fname)
        if filename in recent_files:
            recent_files.remove(filename)
        elif folder_name in recent_files:
            recent_files.remove(folder_name)
        recent_files.insert(0, filename)
        recent_files = recent_files[:5]

        with open(recent_files_path, "w") as f:
            json.dump(recent_files, f, indent=4)
    
    def weighted_graph(self):
        g = {}
        for i in self.items():
            if isinstance(i, NodeItem):
                g[i] = []
            elif isinstance(i, EdgeItem):
                dist = i.laenge()
                g[i.start_node].append((i.end_node, dist))
                if not getattr(i, 'directed', False):
                    g[i.end_node].append((i.start_node, dist))
        return g
    
    def show_distance(self, text):
        self.win.dist_label.setText(text)
    
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