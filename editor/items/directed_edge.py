import math
from editor.items.edge import EdgeItem
from PyQt6.QtGui import QPainter, QPen, QPolygonF, QBrush, QColor
from PyQt6.QtCore import QPointF

class DirectedEdgeItem(EdgeItem):
    def custom_init(self, custom_param):
        self.directed = True
    
    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        start_scene = self.start_node.sceneBoundingRect().center()
        end_scene = self.end_node.sceneBoundingRect().center()

        dx = end_scene.x() - start_scene.x()
        dy = end_scene.y() - start_scene.y()
        length = math.hypot(dx, dy)

        if length == 0:
            return

        end_rect = self.end_node.sceneBoundingRect()
        node_radius = (min(end_rect.width(), end_rect.height()) / 2) - 5

        ratio = (length - node_radius) / length
        tip_scene = QPointF(
            start_scene.x() + dx * ratio,
            start_scene.y() + dy * ratio
        )

        start = self.mapFromScene(start_scene)
        end = self.mapFromScene(tip_scene)

        self.arrow_size = 18.0
        self._draw_arrowhead(painter, start, end)
    
    def boundingRect(self):
        extra = getattr(self, 'arrow_size', 18.0) + 2.0
        return super().boundingRect().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        from PyQt6.QtGui import QPainterPathStroker
        stroker = QPainterPathStroker()
        stroker.setWidth(self.p_width + getattr(self, 'arrow_size', 18.0))
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
        painter.setPen(QPen(QColor(self.color), 1))
        painter.drawPolygon(QPolygonF([tip, p1, p2]))