from PyQt6.QtWidgets import QMenu, QFileDialog
from PyQt6.QtGui import QAction

class ExportMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__("Export", parent)
        self.setObjectName("exportMenu")
        self.init_ui()

    def init_ui(self):
        self.export_png_action = QAction("Export whole scene", self)
        self.export_png_action.triggered.connect(self.export_whole_scene)
        self.addAction(self.export_png_action)

        self.export_selected_action = QAction("Export selected part", self)
        self.export_selected_action.triggered.connect(self.export_part)
        self.addAction(self.export_selected_action)

    def export_whole_scene(self):
        file_path = self.get_file_path()
        if file_path:
            self.parent().scene().export_png(file_path)

    def export_part(self):
        self.parent().begin_export_selection()

    def get_file_path(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export as PNG", "", "PNG Files (*.png)"
        )
        return file_path