from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QMenu, QColorDialog, QInputDialog
from PyQt6.QtGui import QPainterPath, QPen, QColor
from PyQt6.QtCore import QTimer

class EdgeItem(QGraphicsPathItem):
    def __init__(self, start_node, end_node, color=QColor(255, 255, 255), path_width=12):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        # Edge in beiden Nodes registrieren
        start_node.edges.append(self)
        end_node.edges.append(self)

        self.setZValue(-1)  # hinter Nodes zeichnen
        self.p_width = path_width
        self.color = color
        self.colour = [color.red(), color.green(), color.blue()]
        self.setPen(QPen(color, path_width))

        self.update_position()

    def update_position(self):
        start = self.start_node.sceneBoundingRect().center()
        end = self.end_node.sceneBoundingRect().center()

        path = QPainterPath()
        path.moveTo(start)
        path.lineTo(end)

        self.setPath(path)
    
    def laenge(self): # Länge des Edges zurückgeben
        start = self.start_node.sceneBoundingRect().center()
        end = self.end_node.sceneBoundingRect().center()
        return ((start.x() - end.x()) ** 2 + (start.y() - end.y()) ** 2) ** 0.5
    
    def change_color(self):
        scene = self.scene()
        if not scene:
            return

        views = scene.views()
        if not views:
            return

        parent = views[0]

        new_color = QColorDialog.getColor(
            self.color,
            parent,
            "Farbe wählen"
        )
        
        if not new_color.isValid():
            return
        
        self.color = QColor(new_color)
        self.set_pen()
        self.colour = [self.color.red(), self.color.green(), self.color.blue()]
        self.update()
    
    def request_color_change(self):
        QTimer.singleShot(0, self.change_color)

    def set_pen(self):
        self.setPen(QPen(self.color, self.p_width))
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = menu.addAction("Löschen")
        color_action = menu.addAction("Farbe ändern")
        width_action = menu.addAction("Dicke ändern")

        action = menu.exec(event.screenPos())

        # Aktion 1: Löschen
        if action == delete_action:
            scene = self.scene()
            scene.removeItem(self)
            return
        
        # Aktion 2: Farbe ändern
        if action == color_action:
            self.request_color_change()
        
        # Aktion 3: Dicke ändern
        if action == width_action:
            new_width, ok = QInputDialog.getDouble(
                None, "Breite ändern", "Breite: "
            )
            if new_width and ok:
                self.p_width = new_width
                self.set_pen()