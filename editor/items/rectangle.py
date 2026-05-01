from PyQt6.QtGui import QPainter, QPen, QColor
from editor.items.node import NodeItem

class NodeRect(NodeItem):
    """A single rectangular node in the diagram."""
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffffff"), 3))
            self.resize_handle.show()
        else:
            painter.setPen(self.pen)
            self.resize_handle.hide()
        painter.setBrush(self.brush)
        painter.drawRect(self.boundingRect())
