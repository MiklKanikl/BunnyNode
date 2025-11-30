from PyQt6.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem, QColorDialog,
    QInputDialog, QMenu, QGraphicsPathItem, QGraphicsItem
)
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QCursor, QAction, QPainterPath
from PyQt6.QtCore import Qt, QPointF

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
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = menu.addAction("Löschen")

        action = menu.exec(event.screenPos())

        # Aktion 1: Löschen
        if action == delete_action:
            scene = self.scene()
            scene.removeItem(self)
            return

class NodeRect(QGraphicsRectItem):
    """Ein einzelnes verschiebbares und beschriftbares Rechteck."""
    _id_counter = 1

    def __init__(self, x, y, w, h, color):
        super().__init__(0, 0, w, h)
        self.id = NodeRect._id_counter
        NodeRect._id_counter += 1
        self.edges = []
        self.setPos(x, y)
        self.colour = [color.red(), color.green(), color.blue()]

        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Farbe + Rahmen
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("black"), 2))

        # Textobjekt in der Mitte
        self.label = QGraphicsTextItem("", self)
        self.text = ""
        self.label.setDefaultTextColor(QColor("white"))
        self.updateLabelPosition()
    
    def update_text(self, new_text):
        self.text = new_text
        self.label.setPlainText(new_text)
        self.updateLabelPosition()
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Edges informieren, dass sie sich neu zeichnen müssen
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def updateLabelPosition(self):
        """Text in die Mitte platzieren."""
        rect = self.rect()
        text_rect = self.label.boundingRect()
        x = (rect.width() - text_rect.width()) / 2
        y = (rect.height() - text_rect.height()) / 2
        self.label.setPos(x, y)

    def mouseDoubleClickEvent(self, event):
        """Doppelklick → Beschriftung ändern."""
        new_text, ok = QInputDialog.getText(None, "Beschriftung eingeben", "Text:")
        if ok and new_text.strip():
            self.label.setPlainText(new_text)
            self.text = new_text
            self.updateLabelPosition()
        super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Löschen", menu)
        rename_action = QAction("Umbenennen", menu)
        color_action  = QAction("Farbe ändern", menu)
        edge_del_action = QAction("Kanten löschen", menu)

        menu.addAction(delete_action)
        menu.addAction(rename_action)
        menu.addAction(color_action)
        menu.addAction(edge_del_action)

        action = menu.exec(event.screenPos())

        # Aktion 1: Löschen
        if action == delete_action:
            scene = self.scene()
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
            new_color = QColorDialog.getColor()
            if new_color.isValid():
                self.setBrush(new_color)
                self.color = new_color
                self.colour = [new_color.red(), new_color.green(), new_color.blue()]
            return
        
        # Aktion 4: Kanten löschen
        if action == edge_del_action:
            scene = self.scene()
            for edge in self.edges[:]:
                scene.removeItem(edge)
            return

class NodeEllipse(QGraphicsEllipseItem):
    """Ein einzelner verschiebbarer Kreis."""
    _id_counter = 1

    def __init__(self, x, y, w, h, color):
        super().__init__(0, 0, w, h)
        self.id = NodeEllipse._id_counter + NodeRect._id_counter
        NodeEllipse._id_counter += 1
        self.edges = []
        self.setPos(x, y)
        self.colour = [color.red(), color.green(), color.blue()]

        self.setFlags(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        # Farbe + Rahmen
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("black"), 2))

        # Textobjekt in der Mitte
        self.label = QGraphicsTextItem("", self)
        self.text = ""
        self.label.setDefaultTextColor(QColor("white"))
        self.updateLabelPosition()
    
    def update_text(self, new_text):
        self.text = new_text
        self.label.setPlainText(new_text)
        self.updateLabelPosition()
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Edges informieren, dass sie sich neu zeichnen müssen
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)
    
    def updateLabelPosition(self):
        """Text in die Mitte platzieren."""
        ellp_rect = self.rect()
        text_rect = self.label.boundingRect()
        x = (ellp_rect.width() - text_rect.width()) / 2
        y = (ellp_rect.height() - text_rect.height()) / 2
        self.label.setPos(x, y)
    
    def mouseDoubleClickEvent(self, event):
        """Doppelklick → Beschriftung ändern."""
        new_text, ok = QInputDialog.getText(None, "Beschriftung eingeben", "Text:")
        if ok and new_text.strip():
            self.label.setPlainText(new_text)
            self.text = new_text
            self.updateLabelPosition()
        super().mouseDoubleClickEvent(event)
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Löschen", menu)
        rename_action = QAction("Umbenennen", menu)
        color_action  = QAction("Farbe ändern", menu)
        edge_del_action = QAction("Kanten löschen", menu)

        menu.addAction(delete_action)
        menu.addAction(rename_action)
        menu.addAction(color_action)
        menu.addAction(edge_del_action)

        action = menu.exec(event.screenPos())

        # Aktion 1: Löschen
        if action == delete_action:
            scene = self.scene()
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
            new_color = QColorDialog.getColor()
            if new_color.isValid():
                self.setBrush(new_color)
                self.color = new_color
                self.colour = [new_color.red(), new_color.green(), new_color.blue()]
            return
        
        # Aktion 4: Kanten löschen
        if action == edge_del_action:
            scene = self.scene()
            for edge in self.edges[:]:
                scene.removeItem(edge)
            return