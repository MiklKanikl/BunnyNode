from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QMenu, QColorDialog, QInputDialog
from PyQt6.QtGui import QPainterPath, QPen, QColor
from PyQt6.QtCore import QTimer

class EdgeItem(QGraphicsPathItem):
    def __init__(self, start_node, end_node, color=QColor(0, 0, 0), path_width=6, custom_param=[]):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.directed = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        start_node.edges.append(self)
        end_node.edges.append(self)

        self.setZValue(-1)
        self.p_width = path_width
        self.color = color
        self.colour = [color.red(), color.green(), color.blue()]
        self.setPen(QPen(color, path_width))

        self.update_position()
        self.custom_init(custom_param)
    
    def custom_init(self, custom_param):
        pass

    def update_position(self):
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
            "Choose color"
        )
        
        if not new_color.isValid():
            return
        
        self.scene().controller.change_color(self, self.color, new_color)
    
    def apply_color(self, color: QColor):
        self.color = QColor(color)
        self.set_pen()
        self.colour = [self.color.red(), self.color.green(), self.color.blue()]
        self.update()
    
    def request_color_change(self):
        QTimer.singleShot(0, self.change_color)

    def set_pen(self):
        self.setPen(QPen(self.color, self.p_width))
    
    def apply_width(self, width):
        self.p_width = width
        self.set_pen()
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = menu.addAction("Delete")
        color_action = menu.addAction("Change color")
        width_action = menu.addAction("Change width")

        action = menu.exec(event.screenPos())
        scene = self.scene()

        # Aktion 1: Löschen
        if action == delete_action:
            scene.controller.delete_node(scene, [self])
            return
        
        # Aktion 2: Farbe ändern
        if action == color_action:
            self.request_color_change()
        
        # Aktion 3: Dicke ändern
        if action == width_action:
            new_width, ok = QInputDialog.getDouble(
                None, "Change width", "Width: "
            )
            if new_width and ok:
                scene.controller.resize_edge(self, self.p_width, new_width)