from PyQt6.QtGui import QUndoCommand

class ResizeNodeCommand(QUndoCommand):
    def __init__(self, node, old_w, old_h, new_w, new_h):
        super().__init__("Resize Node")
        self.node = node
        self.old_w = old_w
        self.old_h = old_h
        self.new_w = new_w
        self.new_h = new_h
        self.resized = False
    
    def redo(self):
        if not self.resized:
            self.node.resize(self.new_h, self.new_w)
            self.resized = True
    
    def undo(self):
        self.node.resize(self.old_h, self.old_w)
        self.resized = False