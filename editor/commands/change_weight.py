from PyQt6.QtGui import QUndoCommand

class ChangeWeightCommand(QUndoCommand):
    def __init__(self, item, old_weight, new_weight):
        super().__init__()
        self.item = item
        self.old_weight = old_weight
        self.new_weight = new_weight

    def undo(self):
        self.item.weight = self.old_weight

    def redo(self):
        self.item.weight = self.new_weight