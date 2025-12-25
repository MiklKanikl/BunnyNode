from PyQt6.QtWidgets import QGraphicsView, QFileDialog
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter
import os

class DiagramView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setWindowTitle("Diagram Editor")
        self.setRenderHints(QPainter.RenderHint.Antialiasing |
                            QPainter.RenderHint.SmoothPixmapTransform)

        self.zoom = 0
        self.zoom_step = 0.1
        self.zoom_range = [-5, 5]   # Min/Max Zoom

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._panning = False
        self._pan_start = QPoint()
    
    def create_rect(self):
        self.scene().add_rect(0, 0)
    
    def create_ellipse(self):
        self.scene().add_ellipse(0, 0)
    
    def save_diagram(self):
        self.scene().save_file_dialog()
    
    def load_a_diagram(self):
        self.scene().load_file_dialog()
    
    def export(self):
        folder = "exports"
        os.makedirs(folder, exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Diagramm exportieren",
            folder,
            f"*.png"
        )

        if not path:
            return
        
        self.scene().export_png(path)

    #ZOOM
    def wheelEvent(self, event):
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

    #PAN
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
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_P and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.export()
        return super().keyPressEvent(event)