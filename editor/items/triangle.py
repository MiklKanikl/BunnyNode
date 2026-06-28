from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygonF
from editor.calculations.node_dist_calculator import ShapeBorderCalculator
from editor.items.node import NodeItem

class NodeTriangle(NodeItem):
    """A single triangular node in the diagram."""
    def custom_init(self, custom_param):
        self.typ = "triangle"

    def createPolygon(self):
        points = [
            QPointF(0, -self.height / 2),
            QPointF(self.width / 2, self.height / 2),
            QPointF(-self.width / 2, self.height / 2)
        ]
        return QPolygonF(points)
    
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffffff"), 3))
            self.resize_handle.show()
        else:
            painter.setPen(self.pen)
            self.resize_handle.hide()
        painter.setBrush(self.brush)
        painter.drawPolygon(self.createPolygon())
    
    def contains(self, point):
        return self.createPolygon().containsPoint(point, Qt.FillRule.WindingFill)
    
    def get_distance_center_border(self, angle):
        return ShapeBorderCalculator.triangle(self.width, self.height, angle)