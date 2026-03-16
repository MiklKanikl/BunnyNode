from PyQt6.QtGui import QUndoCommand

class PasteCommand(QUndoCommand):
    def __init__(self, scene):
        super().__init__("Paste")
        self.scene = scene
        self.added_items = self.scene.controller.clipboard.paste()
        self.added = False
    
    def redo(self):
        if not self.added:
            for item in self.added_items:
                self.scene.addItem(item)
            self.added = True
    
    def undo(self):
        if self.added:
            for item in self.added_items:
                self.scene.removeItem(item)
            self.added = False