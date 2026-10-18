from PyQt6.QtGui import QUndoCommand

class ReconnectEdgeCommand(QUndoCommand):
    def __init__(self, edge, endpoint, old_node, new_node):
        super().__init__("Reconnect Edge")
        self.edge = edge
        self.endpoint = endpoint
        self.old_node = old_node
        self.new_node = new_node

    def redo(self):
        self.edge.set_endpoint(self.endpoint, self.new_node)

    def undo(self):
        self.edge.set_endpoint(self.endpoint, self.old_node)
