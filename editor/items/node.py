from PyQt6.QtWidgets import (
    QGraphicsTextItem, QInputDialog,
    QMenu, QGraphicsItem, QColorDialog, QDialog
)
from PyQt6.QtGui import QColor, QBrush, QPen, QAction, QPainter
from PyQt6.QtCore import Qt, QRectF, QTimer

class NodeRect(QGraphicsItem):
    """Ein einzelner verschiebbarer und beschriftbarer Rechtecksknoten."""
    _id_counter = 0

    def __init__(self, x, y, w, h, color):
        self.width = float(w)
        self.height = float(h)
        super().__init__()
        self.id = NodeRect._id_counter + NodeEllipse._id_counter
        NodeRect._id_counter += 1
        self.edges = []
        self.setPos(x, y)
        self.color = QColor(color)
        self.colour = [color.red(), color.green(), color.blue()]

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Farbe + Rahmen
        self.pen = QPen(QColor("black"), 2)
        self.brush = QBrush(self.color)

        # Textobjekt in der Mitte
        self.label = QGraphicsTextItem("", self)
        self.text = ""
        self.label.setDefaultTextColor(QColor("white"))
        self.updateLabelPosition()
    
    def boundingRect(self):
        return QRectF(0.0, 0.0, self.width, self.height)
    
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isSelected():
            painter.setPen(QPen(QColor("#3fa9f5"), 3))
        else:
            painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRect(self.boundingRect())

    def update_text(self, new_text):
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
            self.label.setPlainText(new_text)
            self.text = new_text
            self.updateLabelPosition()
        super().mouseDoubleClickEvent(event)
    
    # Farbänderungslogik
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
            "Farbe wählen"
        )
        
        if not new_color.isValid():
            return

        self.apply_color(new_color)

    def request_color_change(self):
        QTimer.singleShot(0, self.open_color_dialog)
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Löschen", menu)
        rename_action = QAction("Umbenennen", menu)
        color_action  = QAction("Farbe ändern", menu)
        size_action = QAction("Größe ändern", menu)
        edge_del_action = QAction("Kanten löschen", menu)
        startnode_action = QAction("Startnode wählen", menu)
        endnode_action = QAction("Endnode wählen", menu)

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
            for edge in self.edges[:]:
                scene.removeItem(edge)
            scene.removeItem(self)
            return

        # Aktion 2: Umbenennen
        if action == rename_action:
            new_text, ok = QInputDialog.getText(
                None, "Umbenennen", "Neuer Name:"
            )
            if ok and new_text.strip():
                self.label.setPlainText(new_text)
                self.updateLabelPosition()
            return

        # Aktion 3: Farbe ändern
        if action == color_action:
            #self.request_color_change()
            self.open_color_dialog()
            return
        
        # Aktion 4: Kanten löschen
        if action == edge_del_action:
            for edge in self.edges[:]:
                scene.removeItem(edge)
            return
        
        # Aktion 5: Größe ändern
        if action == size_action:
            new_width, ok = QInputDialog.getDouble(
                None, "Größe ändern", "Breite:"
            )
            new_height, ok = QInputDialog.getDouble(
                None, "Größe ändern", "Höhe"
            )
            if ok and new_width and new_height:
                self.prepareGeometryChange()
                self.width = float(new_width)
                self.height = float(new_height)
                self.update()
            return
        
        # Aktion 6: Node als Startnode für Distanzrechnung wählen
        if action == startnode_action:
            scene.startnode = self
            return

        # Aktion 7: Node als Endnode für Distanzrechnung wählen
        if action == endnode_action:
            scene.endnode = self
            return

class NodeEllipse(QGraphicsItem):
    """Ein einzelner verschiebbarer Kreisknoten."""
    _id_counter = 0

    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.width = float(w)
        self.height = float(h)
        self.color = QColor(color)
        self.id = NodeEllipse._id_counter + NodeRect._id_counter
        NodeEllipse._id_counter += 1
        self.edges = []
        self.setPos(x, y)
        self.colour = [color.red(), color.green(), color.blue()]

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Farbe + Rahmen
        self.brush = QBrush(self.color)
        self.pen = QPen(Qt.GlobalColor.black, 2)

        # Textobjekt in der Mitte
        self.label = QGraphicsTextItem("", self)
        self.text = ""
        self.label.setDefaultTextColor(QColor("white"))
        self.updateLabelPosition()
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.setPen(QPen(QColor("#3fa9f5"), 3))
        else:
            painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawEllipse(self.boundingRect())
    
    def update_text(self, new_text):
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
            self.label.setPlainText(new_text)
            self.text = new_text
            self.updateLabelPosition()
        super().mouseDoubleClickEvent(event)
    
    # Farbänderungslogik
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
            "Farbe wählen"
        )
        
        if not new_color.isValid():
            return

        self.apply_color(new_color)

    def request_color_change(self):
        QTimer.singleShot(0, self.open_color_dialog)
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Löschen", menu)
        rename_action = QAction("Umbenennen", menu)
        color_action  = QAction("Farbe ändern", menu)
        edge_del_action = QAction("Kanten löschen", menu)
        size_action = QAction("Größe ändern", menu)
        startnode_action = QAction("Startnode wählen", menu)
        endnode_action = QAction("Endnode wählen", menu)

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
            for edge in self.edges[:]:
                scene.removeItem(edge)
            scene.removeItem(self)
            return

        # Aktion 2: Umbenennen
        if action == rename_action:
            new_text, ok = QInputDialog.getText(
                None, "Umbenennen", "Neuer Name:"
            )
            if ok and new_text.strip():
                self.label.setPlainText(new_text)
                self.updateLabelPosition()
            return

        # Aktion 3: Farbe ändern
        if action == color_action:
            self.request_color_change()
            return
        
        # Aktion 4: Kanten löschen
        if action == edge_del_action:
            for edge in self.edges[:]:
                scene.removeItem(edge)
            return
        
        # Aktion 5: Größe ändern
        if action == size_action:
            new_width, ok = QInputDialog.getDouble(
                None, "Größe ändern", "Breite:"
            )
            new_height, ok = QInputDialog.getDouble(
                None, "Größe ändern", "Höhe"
            )
            if ok and new_width and new_height:
                self.prepareGeometryChange()
                self.width = float(new_width)
                self.height = float(new_height)
                self.update()
            return
        
        # Aktion 6: Node als Startnode für Distanzrechnung wählen
        if action == startnode_action:
            scene.startnode = self
            return

        # Aktion 7: Node als Endnode für Distanzrechnung wählen
        if action == endnode_action:
            scene.endnode = self
            return