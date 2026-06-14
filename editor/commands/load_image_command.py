from PyQt6.QtGui import QUndoCommand

class LoadImageCommand(QUndoCommand):
    def __init__(self, node, old_width, old_height, old_file_path, file_path):
        super().__init__("Load Image")
        self.node = node
        self.file_path = file_path
        self.old_file_path = old_file_path
        self.old_width = old_width
        self.old_height = old_height
        self.loaded = False

    def redo(self):
        if not self.loaded:
            self.node.load_image(self.file_path)
            self.loaded = True
    
    def undo(self):
        self.node.resize(self.old_height, self.old_width)
        self.node.load_image(self.old_file_path)
        self.loaded = False