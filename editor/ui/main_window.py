from PyQt6.QtWidgets import QMainWindow, QToolBar, QStatusBar, QLabel
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QIcon
from editor.resources import icon
from editor.controller.app_controller import AppController

class EditorWindow(QMainWindow):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle("Diagrammeditor")
        self.setWindowIcon(QIcon(icon("window.png")))
        self.setCentralWidget(view)
        self.build_toolbar()
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
    
    def build_toolbar(self):
        tb = QToolBar("Werkzeuge", self)
        tb.setIconSize(QSize(32, 32))
        self.addToolBar(tb)

        add_rect = QAction(QIcon(icon("add_rect.png")), "Rechteck", self)
        add_ellipse = QAction(QIcon(icon("add_ellipse.png")), "Kreis", self)
        save = QAction(QIcon(icon("save.png")), "Speichern", self)
        load = QAction(QIcon(icon("load.png")), "Laden", self)
        export_png = QAction(QIcon(icon("export.png")), "PNG exportieren", self)
        dist = QAction(QIcon(icon("distance.png")), "Entfernung", self)

        tb.addAction(add_rect)
        tb.addAction(add_ellipse)
        tb.addAction(save)
        tb.addAction(load)
        tb.addAction(export_png)
        tb.addAction(dist)

        add_rect.triggered.connect(self.centralWidget().create_rect)
        add_ellipse.triggered.connect(self.centralWidget().create_ellipse)
        save.triggered.connect(self.centralWidget().save_diagram)
        load.triggered.connect(self.centralWidget().load_a_diagram)
        export_png.triggered.connect(self.centralWidget().export)
        dist.triggered.connect(self.centralWidget().compute_distance)

        self.setStatusBar(QStatusBar(self))
        self.status = QLabel("Bereit")
        self.statusBar().addPermanentWidget(self.status)