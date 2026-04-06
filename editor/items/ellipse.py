from PyQt6.QtGui import QPainter, QPen, QColor
from editor.items.node import NodeItem

class NodeEllipse(NodeItem):
    """A single elliptical node in the diagram."""
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffffff"), 3))
        else:
            painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawEllipse(self.boundingRect())