from PyQt6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QLabel
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QIcon
from editor.resources import icon
from editor.controller.app_controller import AppController

class EditorWindow(QMainWindow):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle("Diagrameditor")
        self.setWindowIcon(QIcon(icon("window.png")))
        self.setCentralWidget(view)
        self.build_menubar()
        self.controller = AppController()
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
        toolbar = self.addToolBar("Edit")
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
    
    def build_menubar(self):
        menu = self.menuBar()

        add_menu = menu.addMenu("&New")
        file_menu = menu.addMenu("&File")
        calc_menu = menu.addMenu("&Calc")

        add_rect = QAction(QIcon(icon("add_rect.png")), "Rectangle", self)
        add_menu.addAction(add_rect)
        add_rect.triggered.connect(self.centralWidget().create_rect)

        add_ellipse = QAction(QIcon(icon("add_ellipse.png")), "Ellipse", self)
        add_menu.addAction(add_ellipse)
        add_ellipse.triggered.connect(self.centralWidget().create_ellipse)

        add_image = QAction(QIcon(icon("add_image.png")), "Image", self)
        add_menu.addAction(add_image)
        add_image.triggered.connect(self.centralWidget().create_image)

        save = QAction(QIcon(icon("save.png")), "Save", self)
        file_menu.addAction(save)
        save.triggered.connect(self.centralWidget().save_diagram)

        load = QAction(QIcon(icon("load.png")), "Load", self)
        file_menu.addAction(load)
        load.triggered.connect(self.centralWidget().load_a_diagram)

        export_png = QAction(QIcon(icon("export.png")), "Export PNG", self)
        file_menu.addAction(export_png)
        export_png.triggered.connect(self.centralWidget().export)

        dist = QAction(QIcon(icon("distance.png")), "Distance", self)
        calc_menu.addAction(dist)
        dist.triggered.connect(self.centralWidget().compute_distance)

        self.setStatusBar(QStatusBar(self))
        self.status = QLabel("Ready")
        self.statusBar().addPermanentWidget(self.status)