import math
from editor.items.edge import EdgeItem
from PyQt6.QtGui import QPainter, QPolygonF, QBrush, QColor
from PyQt6.QtCore import QPointF, Qt

class DirectedEdgeItem(EdgeItem):
    def custom_init(self, custom_param):
        self.directed = True

    @property
    def arrow_size(self):
        return self.p_width * 3.0
    
    def paint(self, painter, option, widget=None):
        start_scene = self.start_node.sceneBoundingRect().center()
        end_scene = self.end_node.sceneBoundingRect().center()

        dx = end_scene.x() - start_scene.x()
        dy = end_scene.y() - start_scene.y()
        length = math.hypot(dx, dy)

        if length == 0:
            return

        angle = math.atan2(dy, dx)
        node_dist = self.end_node.get_distance_center_border(angle) - 2.5

        ratio = (length - node_dist) / length
        tip_scene = QPointF(
            start_scene.x() + dx * ratio,
            start_scene.y() + dy * ratio
        )

        start = self.mapFromScene(start_scene)
        end = self.mapFromScene(tip_scene)

        head_length = self.arrow_size * math.cos(math.pi / 6)
        head_angle = math.atan2(end.y() - start.y(), end.x() - start.x())
        base = QPointF(
            end.x() - head_length * math.cos(head_angle),
            end.y() - head_length * math.sin(head_angle)
        )

        painter.save()
        painter.setPen(self.pen())
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(start, base)
        self._draw_arrowhead(painter, start, end)
        painter.restore()
    
    def boundingRect(self):
        extra = self.arrow_size + 2.0
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        from PyQt6.QtGui import QPainterPathStroker
        stroker = QPainterPathStroker()
        stroker.setWidth(self.p_width + self.arrow_size)
        return stroker.createStroke(self.path())
    
    def _draw_arrowhead(self, painter, start, end):
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.hypot(dx, dy)

        if length == 0:
            return

        angle = math.atan2(dy, dx)

        tip = end

        p1 = QPointF(
            tip.x() - self.arrow_size * math.cos(angle - math.pi / 6),
            tip.y() - self.arrow_size * math.sin(angle - math.pi / 6)
        )
        p2 = QPointF(
            tip.x() - self.arrow_size * math.cos(angle + math.pi / 6),
            tip.y() - self.arrow_size * math.sin(angle + math.pi / 6)
        )

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygonF([tip, p1, p2]))