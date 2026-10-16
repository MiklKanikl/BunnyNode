from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QMainWindow

class DockTabsContainer:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.tabs: list[QDockWidget] = []
        self.current_dock: QDockWidget | None = None
        self.main_window.tabifiedDockWidgetActivated.connect(self.update_tab)

    def add_tab(self, dock: QDockWidget, area: Qt.DockWidgetArea) -> None:
        self.main_window.addDockWidget(area, dock)
        if self.tabs:
            self.main_window.tabifyDockWidget(self.tabs[0], dock)
        else:
            self.current_dock = dock
        self.tabs.append(dock)

    def update_tab(self, dock: QDockWidget) -> None:
        if dock in self.tabs:
            self.current_dock = dock

    def remove_tab(self, dock: QDockWidget) -> None:
        if dock not in self.tabs:
            return

        self.tabs.remove(dock)
        self.main_window.removeDockWidget(dock)
        if self.current_dock is dock:
            self.current_dock = self.tabs[0] if self.tabs else None
