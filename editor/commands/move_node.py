from PyQt6.QtGui import QUndoCommand

class MoveNodeCommand(QUndoCommand):
    def __init__(self, nodes, old_poss, new_poss):
        super().__init__("Move Node")
        self.nodes = nodes
        self.old_poss = old_poss
        self.new_poss = new_poss
        self.moved = False
    
    def redo(self):
        if not self.moved:
            for node in self.nodes:
                node.setPos(self.new_poss[self.nodes.index(node)])
                self.moved = True
    
    def undo(self):
        for node in self.nodes:
                node.setPos(self.old_poss[self.nodes.index(node)])
                self.moved = True
        self.moved = False