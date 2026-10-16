from PyQt6.QtWidgets import QGraphicsView, QFileDialog
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter
from editor.path_utils import get_exports_directory
from editor.ui.components.createdock import CREATE_ITEM_MIME_TYPE
import os

class DiagramView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setWindowTitle("Diagram Editor")
        self.setRenderHints(QPainter.RenderHint.Antialiasing |
                            QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setAcceptDrops(True)
        
        self.zoom = 0
        self.zoom_step = 0.1
        self.zoom_range = [-5, 5]
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._panning = False
        self._pan_start = QPoint()
    
    def update_settings_stats(self):
        cur_settings = self.scene().controller.get_current_settings()
        self.zoom_step = 0.1

    def create_rect(self):
        self.scene().add_rect(1500, 1500)
    
    def create_ellipse(self):
        self.scene().add_ellipse(1500, 1500)
    
    def create_image(self):
        self.scene().add_image(1500, 1500)

    def save_diagram(self):
        self.scene().save_file_dialog()
    
    def load_a_diagram(self, popup=True):
        self.scene().controller.clear_history()
        if popup:
            self.scene().load_popup()
        else:
            self.scene().load_file_dialog()
    
    def export(self):
        folder = get_exports_directory()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as PNG",
            folder,
            f"*.png"
        )

        if not path:
            return
        
        self.scene().export_png(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(CREATE_ITEM_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(CREATE_ITEM_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if not mime_data.hasFormat(CREATE_ITEM_MIME_TYPE):
            super().dropEvent(event)
            return

        item_type = bytes(mime_data.data(CREATE_ITEM_MIME_TYPE)).decode("utf-8")
        position = self.mapToScene(event.position().toPoint())
        scene = self.scene()

        if item_type in ("rect", "ellipse", "triangle", "image"):
            x = position.x() - 40
            y = position.y() - 40
            creators = {
                "rect": scene.add_rect,
                "ellipse": scene.add_ellipse,
                "triangle": scene.add_triangle,
                "image": scene.add_image,
            }
            creators[item_type](x, y)
        elif item_type in ("edge", "directed_edge"):
            source = scene.node_at(position)
            if source is None:
                event.ignore()
                return
            scene.begin_edge_drag(source, item_type == "directed_edge")
        else:
            event.ignore()
            return

        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
    
    def compute_distance(self, unweighted=False):
        self.scene().setup_path_compution(unweighted=unweighted)

    # ZOOM
    def wheelEvent(self, event):
        angle = event.angleDelta().y()

        if angle > 0 and self.zoom < self.zoom_range[1]:
            zoom_factor = 1 + self.zoom_step
            self.zoom += 1
        elif angle < 0 and self.zoom > self.zoom_range[0]:
            zoom_factor = 1 / (1 + self.zoom_step)
            self.zoom -= 1
        else:
            return

        self.scale(zoom_factor, zoom_factor)

    # PAN
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if event.button() == Qt.MouseButton.RightButton:
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