from PyQt6.QtWidgets import QGraphicsPixmapItem, QInputDialog, QMenu, QFileDialog
from PyQt6.QtGui import QColor, QPen, QAction, QPixmap, QPainter, QImage
from PyQt6.QtCore import QByteArray, QIODevice, Qt, QBuffer
from editor.resources import icon
from editor.items.node import NodeItem

class ImageNode(NodeItem):
    def custom_init(self, custom_param=[]):
        self.image_item = None
        self.current_pixmap = None
        self.image_base64 = ""
        
        try:
            initial_path = custom_param[0]
            if initial_path.startswith('data:image') or (len(initial_path) > 100 and not initial_path.endswith('.png')):
                self.load_image_from_base64(initial_path)
            else:
                self.load_image(initial_path)
        except (IndexError, TypeError):
            default_icon_path = icon("add_image.png")
            self.load_image(default_icon_path)
        
        self.custom_param = [self.image_base64]
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
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.load_image(file_path)
            if hasattr(self, 'scene') and self.scene() and self.scene().controller:
                self.scene().controller.update_node_image(self, self.image_base64)
    
    def load_image(self, file_path):
        if self.image_item:
            self.scene().removeItem(self.image_item)
            self.image_item = None
        
        previous_size = (int(self.width), int(self.height))
        pixmap = QPixmap(file_path)
        
        if pixmap.isNull():
            return False
        
        self.current_pixmap = pixmap
        self.image_base64 = self.pixmap_to_base64(pixmap)
        
        scaled_pixmap = pixmap.scaled(
            previous_size[0], previous_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_item = QGraphicsPixmapItem(scaled_pixmap, self)
        self.image_item.setPos(0, 0)
        self.image_item.update()
        
        new_width = scaled_pixmap.width()
        new_height = scaled_pixmap.height()
        
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
            self.resize(self.height, self.width)
        
        self.updateLabelPosition()
        self.custom_param = [self.image_base64]
        return True
    
    def load_image_from_base64(self, base64_str):
        if not base64_str:
            default_icon_path = icon("add_image.png")
            self.load_image(default_icon_path)
            return False
        
        if self.image_item:
            self.scene().removeItem(self.image_item)
            self.image_item = None
        
        previous_size = (int(self.width), int(self.height))
        pixmap = self.base64_to_pixmap(base64_str)
        
        if pixmap.isNull():
            return False
        
        self.current_pixmap = pixmap
        self.image_base64 = base64_str
        
        scaled_pixmap = pixmap.scaled(
            previous_size[0], previous_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_item = QGraphicsPixmapItem(scaled_pixmap, self)
        self.image_item.setPos(0, 0)
        self.image_item.update()
        
        new_width = scaled_pixmap.width()
        new_height = scaled_pixmap.height()
        
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
            self.resize(self.height, self.width)
        
        self.updateLabelPosition()
        self.custom_param = [self.image_base64]
        return True
    
    def pixmap_to_base64(self, pixmap, format="PNG"):
        if pixmap.isNull():
            return ""
        
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, format)
        buffer.close()
        
        base64_bytes = byte_array.toBase64()
        return base64_bytes.data().decode('utf-8')
    
    def base64_to_pixmap(self, base64_str):
        if not base64_str:
            return QPixmap()
        
        byte_array = QByteArray.fromBase64(base64_str.encode('utf-8'))
        
        pixmap = QPixmap()
        pixmap.loadFromData(byte_array)
        return pixmap
    
    def get_current_base64(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            return self.pixmap_to_base64(self.current_pixmap)
        return self.image_base64
    
    def resize_image(self):
        if self.image_item and self.current_pixmap and not self.current_pixmap.isNull():
            scaled_pixmap = self.current_pixmap.scaled(
                int(self.width), int(self.height),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_item.setPixmap(scaled_pixmap)
            self.image_item.update()
    
    def reload_image(self):
        if self.image_base64:
            self.load_image_from_base64(self.image_base64)
    
    def resize(self, h, w):
        self.prepareGeometryChange()
        self.width = float(w)
        self.height = float(h)
        self.resize_image()
        self._update_handle_position()
        self.update()
        self.updateLabelPosition()
        for edge in self.edges:
            edge.update_position()
    
    def _update_handle_position(self):
        if not hasattr(self, 'resize_handle') or self.resize_handle is None:
            return
        self.resize_handle.setPos(self.width, self.height)
    
    def get_aspect_ratio(self):
        if self.height > 0:
            return self.width / self.height
        return 1.0
    
    def mouseDoubleClickEvent(self, event):
        self.load_image_dialog()
    
    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("Delete", menu)
        size_action = QAction("Change Size", menu)
        aspect_ratio_size_action = QAction("Change Size keeping aspect ratio", menu)
        edge_del_action = QAction("Delete Edges", menu)
        startnode_action = QAction("Select as Start Node", menu)
        endnode_action = QAction("Select as End Node", menu)
        load_image_action = QAction("Load Image", menu)
        reload_action = QAction("Reload Image", menu)

        menu.addAction(delete_action)
        menu.addAction(edge_del_action)
        menu.addAction(size_action)
        menu.addAction(aspect_ratio_size_action)
        menu.addSeparator()
        menu.addAction(load_image_action)
        menu.addAction(reload_action)
        menu.addSeparator()
        menu.addAction(startnode_action)
        menu.addAction(endnode_action)

        action = menu.exec(event.screenPos())
        scene = self.scene()

        if action == delete_action:
            itemlist = []
            for edge in self.edges[:]:
                itemlist.append(edge)
            itemlist.append(self)
            scene.controller.delete_node(scene, itemlist)
            return
        
        if action == edge_del_action:
            itemlist = []
            for edge in self.edges[:]:
                itemlist.append(edge)
            scene.controller.delete_node(scene, itemlist)
            return
        
        if action == size_action:
            new_width, ok = QInputDialog.getInt(
                None, "Change Size", "Width:", value=int(self.width)
            )
            if ok and new_width:
                new_height, ok = QInputDialog.getInt(
                    None, "Change Size", "Height:", value=int(self.height)
                )
                if ok and new_height:
                    scene.controller.resize_node(self, self.width, self.height, new_width, new_height)
            return
        
        if action == aspect_ratio_size_action:
            new_width, ok = QInputDialog.getInt(
                None, "Change Size", "Width:", value=int(self.width)
            )
            if ok and new_width:
                aspect_ratio = self.get_aspect_ratio()
                new_height = int(new_width / aspect_ratio)
                scene.controller.resize_node(self, self.width, self.height, new_width, new_height)
            return
        
        if action == startnode_action:
            scene.startnode = self
            return

        if action == endnode_action:
            scene.endnode = self
            return
        
        if action == load_image_action:
            self.load_image_dialog()
            return
        
        if action == reload_action:
            self.reload_image()
            return
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': 'image',
            'x': self.pos().x(),
            'y': self.pos().y(),
            'width': self.width,
            'height': self.height,
            'color': self.colour,
            'text': self.text,
            'image_base64': self.get_current_base64(),
            'has_image': bool(self.image_base64)
        }
    
    @staticmethod
    def from_dict(data):
        from PyQt6.QtGui import QColor
        
        node = ImageNode(
            data['x'], data['y'],
            data['width'], data['height'],
            QColor(data['color'][0], data['color'][1], data['color'][2]),
            data['text']
        )
        node.id = data['id']
        
        if data.get('has_image') and data.get('image_base64'):
            node.load_image_from_base64(data['image_base64'])
        
        return node