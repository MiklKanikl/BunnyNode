from PyQt6.QtGui import QUndoCommand

class RenameEdgeCommand(QUndoCommand):
    def __init__(self, edge, old_text, new_text):
        super().__init__("Rename Edge")
        self.edge = edge
        self.old_text = old_text
        self.new_text = new_text

    def redo(self):
        self.edge.apply_text(self.new_text)

    def undo(self):
        self.edge.apply_text(self.old_text)