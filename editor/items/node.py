from PyQt6.QtWidgets import (
    QGraphicsTextItem, QInputDialog,
    QMenu, QGraphicsItem, QColorDialog
)
from PyQt6.QtGui import QColor, QBrush, QPen, QAction, QPainterPath
from PyQt6.QtCore import QRectF, QTimer
from editor.elements.resize_handle import ResizeHandle

import copy

class NodeItem(QGraphicsItem):
    _id_counter = 0

    def __init__(self, x, y, w, h, color, text="", custom_param=[]):
        self.custom_param = custom_param
        self.width = float(w)
        self.height = float(h)
        super().__init__()
        self.id = NodeItem._id_counter
        NodeItem._id_counter += 1
        self.edges = []
        self.setPos(x, y)
        self.color = QColor(color)
        self.colour = [color.red(), color.green(), color.blue()]

        self.typ = ""

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.pen = QPen(QColor("black"), 2)
        self.brush = QBrush(self.color)

        self.text = text
        self.label = QGraphicsTextItem(self.text, self)
        self.label.setDefaultTextColor(QColor("black"))
        self.updateLabelPosition()
        self.custom_init(custom_param)
        self.resize_handle = ResizeHandle(self)
        self._update_handle_position()
    
    def custom_init(self, custom_param):
        pass

    def get_distance_center_border(self, angle):
        return 0.0

    def _update_handle_position(self):
        self.resize_handle.setPos(self.width, self.height)

    def shape(self):
        path = QPainterPath()
        path.addRect(QRectF(0, 0, self.width, self.height))
        return path
    
    def boundingRect(self):
        return QRectF(0.0, 0.0, self.width, self.height)

    def update_text(self, new_text):
        self.scene().controller.rename_node(self, self.text, new_text)
        self.text = new_text
        self.label.setPlainText(new_text)
        self.updateLabelPosition()
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def updateLabelPosition(self):
        text_rect = self.label.boundingRect()
        x = (self.width - text_rect.width()) / 2
        y = (self.height - text_rect.height()) / 2
        self.label.setPos(x, y)

    def mouseDoubleClickEvent(self, event):
        new_text, ok = QInputDialog.getText(None, "Beschriftung eingeben", "Text:")
        if ok and new_text.strip():
            self.update_text(new_text)
        super().mouseDoubleClickEvent(event)
    
    def apply_color(self, color: QColor):
        self.color = QColor(color)
        self.brush = QBrush(self.color)
        self.colour = [self.color.red(), self.color.green(), self.color.blue()]
        self.update()
    
    def open_color_dialog(self):
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
            "Choose Color"
        )
        
        if not new_color.isValid():
            return

        self.scene().controller.change_color(self, self.color, new_color)

    def request_color_change(self):
        QTimer.singleShot(0, self.open_color_dialog)
    
    def resize(self, h, w):
        self.prepareGeometryChange()
        self.width = float(w)
        self.height = float(h)
        self._update_handle_position()
        self.update()
        self.updateLabelPosition()
        for edge in self.edges:
            edge.update_position()

    def update_from_data(self, data):
        self.setPos(data.get('x', self.x()), data.get('y', self.y()))
        if 'width' in data:
            self.width = data['width']
        if 'height' in data:
            self.height = data['height']
        if 'color' in data:
            self.apply_color(QColor(data['color'][0], data['color'][1], data['color'][2]))
        if 'text' in data:
            self.text = data['text']
            self.label.setPlainText(self.text)
            self.updateLabelPosition()
        if 'custom_param' in data:
            self.custom_param = data['custom_param']
        self.update()
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Delete", menu)
        rename_action = QAction("Rename", menu)
        color_action  = QAction("Change Color", menu)
        size_action = QAction("Change Size", menu)
        edge_del_action = QAction("Delete Edges", menu)
        startnode_action = QAction("Select as Start Node", menu)
        endnode_action = QAction("Select as End Node", menu)

        menu.addAction(delete_action)
        menu.addAction(rename_action)
        menu.addAction(color_action)
        menu.addAction(edge_del_action)
        menu.addAction(size_action)
        menu.addAction(startnode_action)
        menu.addAction(endnode_action)

        action = menu.exec(event.screenPos())
        scene = self.scene()

        # Aktion 1: Löschen
        if action == delete_action:
            itemlist = []
            for edge in self.edges[:]:
                itemlist.append(edge)
            itemlist.append(self)
            scene.controller.delete_node(scene, itemlist)
            return

        # Aktion 2: Umbenennen
        if action == rename_action:
            new_text, ok = QInputDialog.getText(
                None, "Rename", "New Name:"
            )
            if ok and new_text.strip():
                self.update_text(new_text)
            return

        # Aktion 3: Farbe ändern
        if action == color_action:
            self.open_color_dialog()
            return
        
        # Aktion 4: Kanten löschen
        if action == edge_del_action:
            itemlist = []
            for edge in self.edges[:]:
                itemlist.append(edge)
            scene.controller.delete_node(scene, itemlist)
            return
        
        # Aktion 5: Größe ändern
        if action == size_action:
            new_width, ok = QInputDialog.getInt(
                None, "Change Size", "Width:"
            )
            new_height, ok = QInputDialog.getInt(
                None, "Change Size", "Height:"
            )
            if ok and new_width and new_height:
                scene.controller.resize_node(self, self.width, self.height, new_width, new_height)
            return
        
        # Aktion 6: Node als Startnode für Distanzrechnung wählen
        if action == startnode_action:
            scene.startnode = self
            return

        # Aktion 7: Node als Endnode für Distanzrechnung wählen
        if action == endnode_action:
            scene.endnode = self
            return

    def to_dict(self):
        return copy.deepcopy({
            'id': self.id,
            'type': self.typ,
            'x': self.pos().x(),
            'y': self.pos().y(),
            'width': self.width,
            'height': self.height,
            'color': [self.color.red(), self.color.green(), self.color.blue()],
            'text': self.text,
            'custom_param': self.custom_param
        })