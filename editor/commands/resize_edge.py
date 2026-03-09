from PyQt6.QtGui import QUndoCommand

class ResizeEdgeCommand(QUndoCommand):
    def __init__(self, edge, old_w, new_w):
        super().__init__("Rename Edge")
        self.edge = edge
        self.old_w = old_w
        self.new_w = new_w
        self.resized = False
    
    def redo(self):
        if not self.resized:
            self.edge.apply_width(self.new_w)
            self.resized = True
    
    def undo(self):
        self.edge.apply_width(self.old_w)
        self.resized = False