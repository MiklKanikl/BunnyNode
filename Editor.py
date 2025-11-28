from PyQt6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QColorDialog, QMenu, QDialog, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QColor, QPainter, QCursor, QAction
from PyQt6.QtCore import Qt, QPoint, QTimer
from Module.NodeItems import NodeRect, NodeEllipse, EdgeItem
import sys, os

class MyScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.current_color = QColor(0, 150, 255)  # Standardfarbe

    def keyPressEvent(self, event):
        #R -> neues Rechteck an Mausposition
        if event.key() == Qt.Key.Key_R:
            view = self.views()[0]
            mouse_pos = view.mapFromGlobal(QCursor.pos())
            pos = view.mapToScene(mouse_pos)

            rect = NodeRect(
                pos.x(), pos.y(),
                140, 70,
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
            self.save_scene(filename)
            popup = QDialog(None)
            popup.setWindowTitle("Szene gespeichert")
            QTimer.singleShot(100, popup.accept)
            popup.exec()
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
            print(item)
            if isinstance(item, NodeRect) or isinstance(item, NodeEllipse):
                print(item)
                node = {
                    "id": item.id,
                    "type": "rect" if isinstance(item, NodeRect) else "ellipse",
                    "x": item.scenePos().x(),
                    "y": item.scenePos().y(),
                    "width": item.rect().width(),
                    "height": item.rect().height(),
                    #"color": item.color,
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
                    QColor(0, 150, 255)
                    ##n["color"]
                )
            elif n["type"] == "ellipse":
                node = NodeEllipse(
                    n["x"], n["y"],
                    n["width"], n["height"],
                    QColor(0, 150, 255)
                    ##n["color"]
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

class GraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing |
                            QPainter.RenderHint.SmoothPixmapTransform)

        self.zoom = 0
        self.zoom_step = 0.1
        self.zoom_range = [-5, 5]   # Min/Max Zoom

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._panning = False
        self._pan_start = QPoint()

    # ---------------------
    #     Z O O M
    # ---------------------
    def wheelEvent(self, event):
        if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # normales Scrollen
            return super().wheelEvent(event)

        angle = event.angleDelta().y()

        if angle > 0 and self.zoom < self.zoom_range[1]:
            zoom_factor = 1 + self.zoom_step
            self.zoom += 1
        elif angle < 0 and self.zoom > self.zoom_range[0]:
            zoom_factor = 1 - self.zoom_step
            self.zoom -= 1
        else:
            return

        # Zoom auf Mausposition
        old_pos = self.mapToScene(event.position().toPoint())
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos

        self.translate(delta.x(), delta.y())

    # ---------------------
    #      P A N
    # ---------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if event.button() == Qt.MouseButton.RightButton:
            # optional: RMB pan
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)

app = QApplication(sys.argv)

scene = MyScene()
scene.setSceneRect(0, 0, 2000, 1600)

view = GraphicsView(scene)
view.showMaximized()
view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
view.setRenderHint(QPainter.RenderHint.Antialiasing)
view.show()

sys.exit(app.exec())