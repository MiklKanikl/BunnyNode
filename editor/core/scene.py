from PyQt6.QtWidgets import QGraphicsScene, QColorDialog, QInputDialog, QDialog, QFileDialog
from PyQt6.QtGui import QColor, QCursor, QImage, QPainter
from PyQt6.QtCore import Qt, QTimer, QRectF
from editor.items.node import NodeRect, NodeEllipse
from editor.items.edge import EdgeItem
import os

class DiagramScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 2000, 2000)
        self.current_color = QColor(0, 150, 255)  # Standardfarbe
    
    def export_png(self, path: str):
        EXPORT_WIDTH = 2000
        EXPORT_HEIGHT = 2000

        image = QImage(
            EXPORT_WIDTH,
            EXPORT_HEIGHT,
            QImage.Format.Format_ARGB32
        )
        image.fill(Qt.GlobalColor.black)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        source_rect = QRectF(-100, -100, EXPORT_WIDTH, EXPORT_HEIGHT)
        target_rect = QRectF(-100, -100, EXPORT_WIDTH, EXPORT_HEIGHT)

        self.render(painter, target_rect, source_rect)

        painter.end()

        image.save(path)
    
    def keyPressEvent(self, event):
        #R -> neues Rechteck an Mausposition
        if event.key() == Qt.Key.Key_R:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            rect = NodeRect(
                pos.x(), pos.y(),
                80, 80,
                self.current_color
            )
            self.addItem(rect)
        #E -> neuer Kreis an Mausposition
        elif event.key() == Qt.Key.Key_E:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            ellipse = NodeEllipse(
                pos.x(), pos.y(),
                80, 80,
                self.current_color
            )
            self.addItem(ellipse)
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
            return
        # Ctrl+O -> Szene laden
        elif event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
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
            return
        super().keyPressEvent(event)
    
    def save_scene(self, filename):
        data = {
            "nodes": [],
            "edges": []
        }
        for item in self.items():
            if isinstance(item, NodeRect) or isinstance(item, NodeEllipse):
                node = {
                    "id": item.id,
                    "type": "rect" if isinstance(item, NodeRect) else "ellipse",
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "width": item.rect().width(),
                    "height": item.rect().height(),
                    "color": item.colour,
                    "text": item.text
                }
                data["nodes"].append(node)

            elif isinstance(item, EdgeItem):
                data["edges"].append({
                    "start": item.start_node.id,
                    "end": item.end_node.id
                })
        import json
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def load_scene(self, filename):
        import json
        with open(filename, "r") as f:
            data = json.load(f)

        self.clear()
        id_map = {}

        # nodes
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

        # edges
        for e in data["edges"]:
            start = id_map[e["start"]]
            end = id_map[e["end"]]
            edge = EdgeItem(start, end)
            self.addItem(edge)