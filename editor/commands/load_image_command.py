from PyQt6.QtGui import QUndoCommand

class LoadImageCommand(QUndoCommand):
    def __init__(self, node, old_width, old_height, old_image_data, new_image_data):
        super().__init__("Load Image")
        self.node = node
        self.old_width = old_width
        self.old_height = old_height
        self.old_image_data = old_image_data
        self.new_image_data = new_image_data

    def redo(self):
        if self.new_image_data:
            if isinstance(self.new_image_data, str):
                if self.new_image_data.endswith('.png'):
                    self.node.load_image(self.new_image_data)
                else:
                    self.node.load_image_from_base64(self.new_image_data)
            self.node.resize(self.node.height, self.node.width)

    def undo(self):
        if self.old_image_data:
            if isinstance(self.old_image_data, str):
                if self.old_image_data.endswith('.png'):
                    self.node.load_image(self.old_image_data)
                else:
                    self.node.load_image_from_base64(self.old_image_data)
        else:
            if self.node.image_item:
                self.node.scene().removeItem(self.node.image_item)
                self.node.image_item = None
            self.node.current_pixmap = None
            self.node.image_base64 = ""
            if hasattr(self.node, 'has_image'):
                self.node.has_image = False
        self.node.resize(self.old_height, self.old_width)