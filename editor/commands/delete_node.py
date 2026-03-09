from PyQt6.QtGui import QUndoCommand

class DeleteNodeCommand(QUndoCommand):
    def __init__(self, scene, itemlist):
        super().__init__("Delete Node")
        self.scene = scene
        self.itemlist = itemlist
        self.removed = False
    
    def redo(self):
        if not self.removed:
            for item in self.itemlist:
                self.scene.removeItem(item)
            self.removed = True
    
    def undo(self):
        for item in self.itemlist:
            self.scene.addItem(item)
        self.removed = False