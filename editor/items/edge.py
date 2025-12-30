from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QMenu
from PyQt6.QtGui import QPainterPath, QPen
from PyQt6.QtCore import Qt

class EdgeItem(QGraphicsPathItem):
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Edge in beiden Nodes registrieren
        start_node.edges.append(self)
        end_node.edges.append(self)

        self.setZValue(-1)  # hinter Nodes zeichnen
        self.setPen(QPen(Qt.GlobalColor.white, 12))

        self.update_position()

    def update_position(self):
        """Wird von Nodes aufgerufen, wenn sich deren Position ändert."""
        start = self.start_node.sceneBoundingRect().center()
        end = self.end_node.sceneBoundingRect().center()

        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(end)

        self.setPath(path)
    
    def laenge(self):
        start = self.start_node.sceneBoundingRect().center()
        end = self.end_node.sceneBoundingRect().center()
        return ((start.x() - end.x()) ** 2 + (start.y() - end.y()) ** 2) ** 0.5
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = menu.addAction("Löschen")

        action = menu.exec(event.screenPos())

        # Aktion 1: Löschen
        if action == delete_action:
            scene = self.scene()
            scene.removeItem(self)
            return