from PyQt6.QtWidgets import QGraphicsEllipseItem
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPen

class EdgeEndpointHandle(QGraphicsEllipseItem):
    def __init__(self, edge, endpoint):
        super().__init__(QRectF(-7, -7, 14, 14))
        self.edge = edge
        self.endpoint = endpoint
        color = QColor("#27ae60") if endpoint == "start" else QColor("#e67e22")
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#ffffff"), 2))
        self.setZValue(1000)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setToolTip(f"Drag to reconnect edge {endpoint}")