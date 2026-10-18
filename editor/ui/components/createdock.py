from PyQt6.QtCore import QByteArray, QMimeData, Qt
from PyQt6.QtGui import QDrag, QIcon
from PyQt6.QtWidgets import QDockWidget, QListWidget, QListWidgetItem

from editor.resources import icon

CREATE_ITEM_MIME_TYPE = "application/x-bunnynode-create-item"

class _CreateListWidget(QListWidget):
    def startDrag(self, _supported_actions):
        item = self.currentItem()
        if item is None:
            return

        mime_data = QMimeData()
        mime_data.setData(
            CREATE_ITEM_MIME_TYPE,
            QByteArray(item.data(Qt.ItemDataRole.UserRole).encode("utf-8")),
        )
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(item.icon().pixmap(32, 32))
        drag.exec(Qt.DropAction.CopyAction)

class Createdock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Create", parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        palette = _CreateListWidget()
        palette.setDragEnabled(True)
        palette.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        entries = (
            ("Rectangle", "rect", "add_rect.png"),
            ("Ellipse", "ellipse", "add_ellipse.png"),
            ("Image", "image", "add_image.png"),
            ("Edge", "edge", "add_edge.png"),
            ("Directed Edge", "directed_edge", "add_directed_edge.png"),
        )
        for label, item_type, icon_name in entries:
            item = QListWidgetItem(label)
            if icon_name:
                item.setIcon(QIcon(icon(icon_name)))
            item.setData(Qt.ItemDataRole.UserRole, item_type)
            item.setToolTip("Drag onto the canvas to create")
            palette.addItem(item)

        self.setWidget(palette)
