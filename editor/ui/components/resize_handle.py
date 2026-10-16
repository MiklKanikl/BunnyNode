from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem
from PyQt6.QtGui import QPen, QBrush, QColor, QCursor
from PyQt6.QtCore import Qt

class ResizeHandle(QGraphicsRectItem):
    HANDLE_SIZE = 8.0

    def __init__(self, parent_node):
        super().__init__(parent_node)
        self.parent_node = parent_node
        s = self.HANDLE_SIZE
        self.setRect(-s / 2, -s / 2, s, s)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(QColor("black"), 1))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, False)
        self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.setZValue(10)
        self._dragging = False

    def mousePressEvent(self, event):
        self._dragging = True
        self._start_mouse = event.scenePos()
        self._start_w = self.parent_node.width
        self._start_h = self.parent_node.height
        event.accept()

    def mouseMoveEvent(self, event):
        if not self._dragging:
            return
        delta = event.scenePos() - self._start_mouse
        new_w = max(5.0, self._start_w + delta.x())
        new_h = max(5.0, self._start_h + delta.y())
        self.parent_node.resize(new_h, new_w)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self.parent_node.scene().controller.resize_node(
                self.parent_node,
                self._start_w, self._start_h,
                self.parent_node.width, self.parent_node.height
            )
        self._dragging = False
        event.accept()