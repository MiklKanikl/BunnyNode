from PyQt6.QtGui import QUndoCommand


class ChangeZOrderCommand(QUndoCommand):
    def __init__(self, item, old_z_value, new_z_value, text):
        super().__init__(text)
        self.item = item
        self.old_z_value = old_z_value
        self.new_z_value = new_z_value

    def redo(self):
        self.item.setZValue(self.new_z_value)

    def undo(self):
        self.item.setZValue(self.old_z_value)
