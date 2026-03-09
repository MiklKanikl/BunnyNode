from PyQt6.QtGui import QUndoCommand

class AddNodeCommand(QUndoCommand):
    def __init__(self, scene, node):
        super().__init__("Add Node")
        self.scene = scene
        self.node = node
        self.added = False
    
    def redo(self):
        if not self.added:
            self.scene.addItem(self.node)
            self.added = True
    
    def undo(self):
        self.scene.removeItem(self.node)
        self.added = False