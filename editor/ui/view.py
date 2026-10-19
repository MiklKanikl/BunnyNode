from PyQt6.QtWidgets import QGraphicsView, QMessageBox, QRubberBand
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF
from PyQt6.QtGui import QPainter
from editor.ui.components.createdock import CREATE_ITEM_MIME_TYPE
from editor.ui.components.exportmenu import ExportMenu

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
        self.zoom_range = [-15, 15]
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._panning = False
        self._pan_start = QPoint()
        self._export_selection_active = False
        self._export_selection_start = QPoint()
        self._export_rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.viewport())
    
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

    def save_diagram_as(self):
        self.scene().save_file_dialog(save_as=True)
    
    def load_a_diagram(self, popup=True):
        self.scene().controller.clear_history()
        if popup:
            self.scene().load_popup()
        else:
            self.scene().load_file_dialog()
    
    def export(self):
        self.export_menu = ExportMenu(self)
        self.export_menu.exec(self.mapToGlobal(self.pos()))

    def begin_export_selection(self):
        self._export_selection_active = True
        self._export_rubber_band.hide()
        self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        window = self.window()
        if hasattr(window, "status"):
            window.status.setText("Drag a rectangle to select the export region; press Esc to cancel")

    def _finish_export_selection(self):
        self._export_selection_active = False
        self._export_rubber_band.hide()
        self.viewport().unsetCursor()
        window = self.window()

        selection = self._export_rubber_band.geometry()
        if selection.width() < 2 or selection.height() < 2:
            if hasattr(window, "status"):
                window.status.setText("idle")
            return

        top_left = self.mapToScene(selection.topLeft())
        bottom_right = self.mapToScene(selection.bottomRight())
        source_rect = self.scene().sceneRect().intersected(
            QRectF(top_left, bottom_right).normalized()
        )
        if source_rect.isEmpty():
            if hasattr(window, "status"):
                window.status.setText("idle")
            return

        file_path = self.export_menu.get_file_path()
        if file_path:
            try:
                self.scene().export_png(file_path, source_rect)
            except (OSError, ValueError) as error:
                QMessageBox.critical(self, "Export Failed", str(error))
        if hasattr(window, "status"):
            window.status.setText("idle")

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
        if self._export_selection_active and event.button() == Qt.MouseButton.LeftButton:
            self._export_selection_start = event.position().toPoint()
            self._export_rubber_band.setGeometry(QRect(self._export_selection_start, self._export_selection_start))
            self._export_rubber_band.show()
            event.accept()
            return

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
        if self._export_selection_active and self._export_rubber_band.isVisible():
            current_pos = event.position().toPoint()
            self._export_rubber_band.setGeometry(
                QRect(self._export_selection_start, current_pos).normalized()
            )
            event.accept()
            return

        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._export_selection_active and event.button() == Qt.MouseButton.LeftButton:
            current_pos = event.position().toPoint()
            self._export_rubber_band.setGeometry(
                QRect(self._export_selection_start, current_pos).normalized()
            )
            self._finish_export_selection()
            event.accept()
            return

        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        if self._export_selection_active and event.key() == Qt.Key.Key_Escape:
            self._export_selection_active = False
            self._export_rubber_band.hide()
            self.viewport().unsetCursor()
            window = self.window()
            if hasattr(window, "status"):
                window.status.setText("idle")
            event.accept()
            return

        if event.key() == Qt.Key.Key_P and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.export()
        return super().keyPressEvent(event)