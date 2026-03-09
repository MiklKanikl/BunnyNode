from PyQt6.QtGui import QUndoCommand

class RenameNodeCommand(QUndoCommand):
    def __init__(self, node, old_text, new_text):
        super().__init__("Rename")
        self.node = node
        self.old_text = old_text
        self.new_text = new_text
        self.renamed = False
    
    def redo(self):
        if not self.renamed:
            self.node.label.setPlainText(self.new_text)
            self.renamed = True
    
    def undo(self):
        self.node.label.setPlainText(self.old_text)
        self.renamed = False