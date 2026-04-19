from PyQt6.QtWidgets import QDockWidget, QListWidget, QMainWindow, QMessageBox, QStatusBar, QLabel, QStackedWidget, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from editor.resources import icon
from editor.ui.welcomescreen import WelcomeScreen
from editor.ui.settings_menu import Settings_menu
from editor.controller.app_controller import AppController

class EditorWindow(QMainWindow):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle("BunnyNode")
        self.setWindowIcon(QIcon(icon("window.png")))
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.welcome_screen = WelcomeScreen(self)
        self.stacked_widget.addWidget(self.welcome_screen)
        self.view = view
        self.stacked_widget.addWidget(view)
        self.settings_menu = Settings_menu(self)
        self.stacked_widget.addWidget(self.settings_menu)
        self.build_menubar()
        self.controller = AppController()
        self.build_toolbar()
        self.create_calc_show_panel()
        self.hide_bars()
    
    def build_toolbar(self):
        undo_action = self.controller.undostack.createUndoAction(
            self, "Undo"
        )
        redo_action = self.controller.undostack.createRedoAction(
            self, "Redo"
        )
        undo_action.setIcon(QIcon(icon("undo.png")))
        redo_action.setIcon(QIcon(icon("redo.png")))
        undo_action.setShortcut("Ctrl+Z")
        redo_action.setShortcut("Ctrl+Y")
        self.toolbar = self.addToolBar("Edit")
        self.toolbar.addAction(undo_action)
        self.toolbar.addAction(redo_action)
    
    def build_menubar(self):
        self.menu = self.menuBar()

        add_menu = self.menu.addMenu("&Item")
        file_menu = self.menu.addMenu("&File")
        calc_menu = self.menu.addMenu("&Calc")
        other_menu = self.menu.addMenu("&Other")

        add_rect = QAction(QIcon(icon("add_rect.png")), "Rectangle", self)
        add_menu.addAction(add_rect)
        add_rect.triggered.connect(self.view.create_rect)

        add_ellipse = QAction(QIcon(icon("add_ellipse.png")), "Ellipse", self)
        add_menu.addAction(add_ellipse)
        add_ellipse.triggered.connect(self.view.create_ellipse)

        add_image = QAction(QIcon(icon("add_image.png")), "Image", self)
        add_menu.addAction(add_image)
        add_image.triggered.connect(self.view.create_image)

        new = QAction(QIcon(icon("new_file.png")), "New", self)
        file_menu.addAction(new)
        new.triggered.connect(lambda: self.exit_popup(0))

        save = QAction(QIcon(icon("save.png")), "Save", self)
        file_menu.addAction(save)
        save.triggered.connect(self.view.save_diagram)

        load = QAction(QIcon(icon("load.png")), "Load", self)
        file_menu.addAction(load)
        load.triggered.connect(lambda: self.view.load_a_diagram(True))

        export_png = QAction(QIcon(icon("export.png")), "Export PNG", self)
        file_menu.addAction(export_png)
        export_png.triggered.connect(self.view.export)

        back_to_welcome = QAction(QIcon(icon("undo.png")), "Exit", self)
        file_menu.addAction(back_to_welcome)
        back_to_welcome.triggered.connect(lambda: self.exit_popup(1))

        dist = QAction(QIcon(icon("distance.png")), "Distance", self)
        calc_menu.addAction(dist)
        dist.triggered.connect(self.view.compute_distance)

        settings = QAction(QIcon(icon("settings.png")), "Settings", self)
        other_menu.addAction(settings)
        settings.triggered.connect(self.open_settings)
    
    def exit_popup(self, action):
        popup = QMessageBox()
        popup.setWindowTitle("Warning")
        popup.setText("Are you sure you want to exit? All unsaved changes will be lost.")
        popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if popup.exec() == QMessageBox.StandardButton.Yes:
            if action == 0:
                self.new_diagram()
            elif action == 1:
                self.back_to_welcome()
    
    def create_calc_show_panel(self):
        self.dock = MyDockWidget("Calc results", self)
        self.dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )

        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.dist_label = QLabel("Waiting for computation...")
        layout.addWidget(self.dist_label)
        layout.addStretch()

        self.dock.setWidget(panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
    
    def back_to_welcome(self):
        self.view.scene().clear()
        self.view.scene().controller.clear_history()
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.hide_bars()
    
    def open_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_menu)
        self.hide_bars()
    
    def new_diagram(self):
        self.view.scene().controller.clear_history()
        self.view.scene().clear()
        self.stacked_widget.setCurrentWidget(self.view)
        self.show_bars()
    
    def open_diagram(self):
        self.stacked_widget.setCurrentWidget(self.view)
        self.view.load_a_diagram(False)
        self.show_bars()
    
    def open_recent_file(self, filename):
        self.stacked_widget.setCurrentWidget(self.view)
        self.view.scene().load_scene(filename)
        self.view.scene().update_recent_files(filename)
        self.show_bars()
    
    def show_bars(self):
        self.dock.show()
        self.menu.show()
        self.toolbar.show()
    
    def hide_bars(self):
        self.dock.hide()
        self.menu.hide()
        self.toolbar.hide()

class MyDockWidget(QDockWidget):
    def closeEvent(self, event):
        event.ignore()