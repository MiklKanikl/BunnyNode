from PyQt6.QtWidgets import QGraphicsScene, QColorDialog, QInputDialog, QDialog, QFileDialog
from PyQt6.QtGui import QColor, QCursor, QImage, QPainter
from PyQt6.QtCore import Qt, QRectF, QTimer
from editor.items.node import NodeRect, NodeEllipse
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
        self.addItem(rect)
    
    def add_ellipse(self, x, y):
        ellp = NodeEllipse(
            x, y,
            80, 80,
            self.current_color
        )
        self.addItem(ellp)
    
    def save_file_dialog(self):
        new_text, ok = QInputDialog.getText(
            None, "Speichern unter", "Dateiname (ohne Endung):", text="diagram"
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
            "Laden",
            folder,                      
            "Diagramm-Dateien (*.diagram *.json)"
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
        #C -> Farbe ändern
        elif event.key() == Qt.Key.Key_C:
            chosen = QColorDialog.getColor(self.current_color)
            if chosen.isValid():
                self.current_color = chosen
            return
        #L -> Kante zwischen zwei ausgewählten Nodes erstellen
        elif event.key() == Qt.Key.Key_L:
            selected = [i for i in self.selectedItems() if isinstance(i, NodeRect) or isinstance(i, NodeEllipse)]
            if len(selected) == 2:
                edge = EdgeItem(selected[0], selected[1])
                self.addItem(edge)
                return
        #Entf -> ausgewählte Items löschen
        elif event.key() == Qt.Key.Key_Delete:
            for item in self.selectedItems():
                if isinstance(item, NodeRect) or isinstance(item, NodeEllipse):
                    for edge in item.edges[:]:
                        self.removeItem(edge)
                    self.removeItem(item)
                elif isinstance(item, EdgeItem):
                    self.removeItem(item)
            return
        # Ctrl+S -> Szene speichern
        elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.save_file_dialog()
            return
        # Ctrl+O -> Szene laden
        elif event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.load_file_dialog()
            return
        super().keyPressEvent(event)
    
    def save_scene(self, filename): # Szene speichern
        data = {
            "nodes": [],
            "edges": []
        }
        for item in self.items():
            if isinstance(item, NodeRect) or isinstance(item, NodeEllipse): # Nodes
                node = {
                    "id": item.id,
                    "type": "rect" if isinstance(item, NodeRect) else "ellipse",
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "width": item.width,
                    "height": item.height,
                    "color": item.colour,
                    "text": item.text
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
                    QColor(n["color"][0], n["color"][1], n["color"][2])
                )
            elif n["type"] == "ellipse":
                node = NodeEllipse(
                    n["x"], n["y"],
                    n["width"], n["height"],
                    QColor(n["color"][0], n["color"][1], n["color"][2])
                )
            node.id = n["id"]
            node.update_text(n.get("text", ""))
            id_map[node.id] = node
            self.addItem(node)

        # Edges
        for e in data["edges"]:
            start = id_map[e["start"]]
            end = id_map[e["end"]]
            color = QColor(e["color"][0], e["color"][1], e["color"][2])
            width = e["width"]
            edge = EdgeItem(start, end, color, width)
            self.addItem(edge)
    
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
            self.show_distance("Kein Pfad")
        else:
            self.show_distance(f"Distanz: {round(d,2)}")
    
    def setup_path_compution(self):
        if self.startnode and self.endnode:
            self.compute_shortest(self.startnode, self.endnode)
        else:
            self.show_distance("Keine Nodes ausgewählt")