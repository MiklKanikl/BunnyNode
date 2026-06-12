from PyQt6.QtWidgets import QGraphicsPixmapItem, QInputDialog, QMenu, QFileDialog
from PyQt6.QtGui import QColor, QPen, QAction, QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from editor.resources import icon
from editor.items.node import NodeItem

class ImageNode(NodeItem):
    """A node that displays an image."""
    def custom_init(self, custom_param=[]):
        self.image_item = None
        try:
            self.img_file = custom_param[0]
        except IndexError:
            self.img_file = icon("add_image.png")
        self.custom_param = [self.img_file]
        self.load_image(self.img_file)
        self.setAcceptDrops(True)
    
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffffff"), 3))
            self.resize_handle.show()
        else:
            painter.setPen(self.pen)
            self.resize_handle.hide()
        painter.setBrush(self.brush)
        painter.drawRect(self.boundingRect())
    
    def load_image_dialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None,
            "Select Image",
            "",
            "Image Files (*.png)"
        )
        if file_path:
            self.img_file = file_path
            self.custom_param = [self.img_file]
            self.scene().controller.load_image(self, self.width, self.height, self.img_file, file_path)
    
    def load_image(self, file_path):
        if self.image_item:
            self.scene().removeItem(self.image_item)
            self.image_item = None
        previous_size = (int(self.width), int(self.height))
        pixmap = QPixmap(file_path)
        self.image_item = QGraphicsPixmapItem(pixmap, self)
        self.image_item.setPos(0, 0)
        scaled_pixmap = pixmap.scaled(previous_size[0], previous_size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_item.setPixmap(scaled_pixmap)
        self.image_item.update()
        self.width = scaled_pixmap.size().width()
        self.height = scaled_pixmap.size().height()
        self.resize(self.height, self.width)
        self.updateLabelPosition()
    
    def resize_image(self):
        if self.image_item:
            previous_size = (int(self.width), int(self.height))
            pixmap = self.image_item.pixmap()
            scaled_pixmap = pixmap.scaled(previous_size[0], previous_size[1], Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_item.setPixmap(scaled_pixmap)
            self.image_item.update()
    
    def reload_image(self):
        if self.image_item:
            previous_size = (int(self.width), int(self.height))
            pixmap = QPixmap(self.img_file)
            scaled_pixmap = pixmap.scaled(previous_size[0], previous_size[1], Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_item.setPixmap(scaled_pixmap)
            self.image_item.update()

    def resize(self, h, w):
        self.prepareGeometryChange()
        self.width = float(w)
        self.height = float(h)
        self.resize_image()
        self._update_handle_position()
        self.update()
        self.reload_image()
        self.updateLabelPosition()
        for edge in self.edges:
            edge.update_position()
    
    def _update_handle_position(self):
        if not hasattr(self, 'resize_handle') or self.resize_handle is None:
            return
        self.resize_handle.setPos(self.width, self.height)
    
    def get_aspect_ratio(self):
        return self.width / self.height
    
    def mouseDoubleClickEvent(self, event):
        pass
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Delete", menu)
        size_action = QAction("Change Size", menu)
        aspect_ratio_size_action = QAction("Change Size keeping aspect ratio", menu)
        edge_del_action = QAction("Delete Edges", menu)
        startnode_action = QAction("Select as Start Node", menu)
        endnode_action = QAction("Select as End Node", menu)
        load_image_action = QAction("load_image", menu)

        menu.addAction(delete_action)
        menu.addAction(edge_del_action)
        menu.addAction(size_action)
        menu.addAction(aspect_ratio_size_action)
        menu.addAction(startnode_action)
        menu.addAction(endnode_action)
        menu.addAction(load_image_action)

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
        
        # Aktion 6: Größe ändern unter Beibehaltung des Seitenverhältnisses
        if action == aspect_ratio_size_action:
            new_width, ok = QInputDialog.getInt(
                None, "Change Size", "Width:"
            )
            if ok and new_width:
                aspect_ratio = self.get_aspect_ratio()
                new_height = int(new_width / aspect_ratio)
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
        
        if action == load_image_action:
            self.load_image_dialog()
            return