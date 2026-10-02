from PyQt6.QtGui import QColor, QUndoCommand


class ChangeTextColorCommand(QUndoCommand):
    def __init__(self, item, old_color: QColor, new_color: QColor):
        super().__init__("Change Text Color")
        self.item = item
        self.old_color = QColor(old_color)
        self.new_color = QColor(new_color)

    def redo(self):
        self.item.apply_text_color(self.new_color)

    def undo(self):
        self.item.apply_text_color(self.old_color)
