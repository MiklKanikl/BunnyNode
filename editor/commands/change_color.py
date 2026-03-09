from PyQt6.QtGui import QUndoCommand

class ChangeColorCommand(QUndoCommand):
    def __init__(self, item, old_color, new_color):
        super().__init__("Change Color")
        self.item = item
        self.old_color = old_color
        self.new_color = new_color
        self.painted = False
    
    def redo(self):
        if not self.painted:
            self.item.apply_color(self.new_color)
            self.painted = True

    def undo(self):
        self.item.apply_color(self.old_color)
        self.painted = False