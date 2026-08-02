from PyQt6.QtGui import QUndoCommand

class LoadImageCommand(QUndoCommand):
    def __init__(self, node, old_width, old_height, old_img_data, new_img_data):
        super().__init__("Load Image")
        self.node = node
        self.new_img_data = new_img_data
        self.old_img_data = old_img_data
        self.old_width = old_width
        self.old_height = old_height
        self.loaded = False

    def redo(self):
        if not self.loaded:
            self.node.load_image(self.new_img_data)
            self.loaded = True
    
    def undo(self):
        if self.loaded:
            self.node.resize(self.old_height, self.old_width)
            self.node.load_image(self.old_img_data)
            self.loaded = False