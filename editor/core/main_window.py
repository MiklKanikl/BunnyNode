from PyQt6.QtWidgets import QInputDialog, QMainWindow, QMessageBox, QStatusBar, QLabel, QStackedWidget, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from editor.resources import icon
from editor.ui.welcomescreen import WelcomeScreen
from editor.ui.settings_menu import Settings_menu
from editor.ui.components.inspectordock import InspectorDock
from editor.ui.components.calcdock import CalcDock
from editor.controller.app_controller import AppController
from editor.client.client import Client

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
        self.build_statusbar()
        self.create_docks()
        self.hide_bars()
        self.online = False
        self.token = None
        self.client = Client()
        self.client.connection_ready.connect(self.on_connection_ready)
        self.client.room_joined.connect(self.on_room_joined)
        self.client.scene_updated.connect(self.on_scene_updated)
        self.client.user_joined.connect(self.on_user_joined)
        self.client.user_left.connect(self.on_user_left)
        self.client.error_occurred.connect(self.on_error)
        self.client.start()
    
    def build_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.status = QLabel("idle")
        self.statusBar().addPermanentWidget(self.status)

    def build_toolbar(self):
        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        undo_action.triggered.connect(self.controller.undostack.undo)
        redo_action.triggered.connect(self.controller.undostack.redo)
        undo_action.setEnabled(self.controller.undostack.canUndo())
        redo_action.setEnabled(self.controller.undostack.canRedo())
        self.controller.undostack.canUndoChanged.connect(undo_action.setEnabled)
        self.controller.undostack.canRedoChanged.connect(redo_action.setEnabled)
        show_token_action = QAction("Show Token", self)
        undo_action.setIcon(QIcon(icon("undo.png")))
        redo_action.setIcon(QIcon(icon("redo.png")))
        undo_action.setShortcut("Ctrl+Z")
        redo_action.setShortcut("Ctrl+Y")
        self.toolbar = self.addToolBar("Edit")
        self.toolbar.addAction(undo_action)
        self.toolbar.addAction(redo_action)
        self.toolbar.addAction(show_token_action)
        show_token_action.triggered.connect(self.show_token)
    
    def build_menubar(self):
        self.menu = self.menuBar()

        add_menu = self.menu.addMenu("&Item")
        actions_menu = self.menu.addMenu("&Actions")
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

        create_edge = QAction(QIcon(icon("add_edge.png")), "Edge", self)
        add_menu.addAction(create_edge)
        create_edge.triggered.connect(lambda: self.view.scene().edge_create_dialog(False))

        create_directed_edge = QAction(QIcon(icon("add_directed_edge.png")), "Directed Edge", self)
        add_menu.addAction(create_directed_edge)
        create_directed_edge.triggered.connect(lambda: self.view.scene().edge_create_dialog(True))

        change_node_color = QAction("Change Node Color", self)
        actions_menu.addAction(change_node_color)
        change_node_color.triggered.connect(lambda: self.view.scene().color_dialog(0))

        change_edge_color = QAction("Change Edge Color", self)
        actions_menu.addAction(change_edge_color)
        change_edge_color.triggered.connect(lambda: self.view.scene().color_dialog(1))

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
    
    def create_docks(self):
        self.calcdock = CalcDock("Calc results", self)
        self.inspectordock = InspectorDock("Inspector", self)

        self.calcdock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        self.inspectordock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.calcdock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspectordock)
    
    def back_to_welcome(self):
        self.view.scene().clear()
        self.view.scene().controller.clear_history()
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.hide_bars()
        self.online = False
        self.token = None
        self.welcome_screen.reload_recent_files()
        self.client.leave_room()
    
    def open_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_menu)
        self.hide_bars()
    
    def new_diagram(self):
        self.view.scene().clear()
        self.stacked_widget.setCurrentWidget(self.view)
        self.show_bars()
    
    def open_diagram(self):
        self.stacked_widget.setCurrentWidget(self.view)
        self.view.load_a_diagram(False)
        self.show_bars()
    
    def create_room(self):
        if self.client.create_room():
            self.token = self.client.room_id
            self.online = True
            self.stacked_widget.setCurrentWidget(self.view)
            self.show_bars()
            self.status.setText(f"Online: Room {self.token}")
        else:
            QMessageBox.critical(self, "Error", "Failed to create room")
    
    def join_collaboration(self):
        token, ok = QInputDialog.getInt(self, "Join Collaboration", "Enter Room Token:")
        if ok and token:
            try:
                self.client.join_room(token)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to join room because {str(e)}")
    
    def open_recent_file(self, filename):
        self.stacked_widget.setCurrentWidget(self.view)
        self.view.scene().load_scene(filename=filename)
        self.view.scene().update_recent_files(filename)
        self.show_bars()
    
    def show_bars(self):
        self.calcdock.show()
        self.inspectordock.show()
        self.menu.show()
        self.toolbar.show()
        self.statusBar().show()
    
    def hide_bars(self):
        self.calcdock.dist_label.setText("Waiting for Computation...")
        self.calcdock.hide()
        self.inspectordock.hide()
        self.menu.hide()
        self.toolbar.hide()
        self.statusBar().hide()
    
    def show_token(self):
        if self.online and self.token:
            t = str(self.token)
        else:
            t = "not in online mode"
        QMessageBox.information(self, "Room Token", f"Current Room Token:\n{t}")
    
    def on_connection_ready(self, ready):
        if ready:
            self.status.setText("Connection ready")
        else:
            self.status.setText("Connection lost")
    
    def on_room_joined(self, data):
        self.token = data.get('room')
        self.online = True
        version = data.get('version', 0)
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        scene_data = {"nodes": nodes, "edges": edges}
        self.view.scene().load_scene(online=True, data=scene_data)
        self.stacked_widget.setCurrentWidget(self.view)
        self.show_bars()
        self.status.setText(f"Online: Room {self.token} (v{version})")
    
    def on_scene_updated(self, data):
        try:
            if data["type"] == "full_state":
                nodes = data.get('nodes', [])
                edges = data.get('edges', [])
                version = data.get('version', 0)
                scene_data = {"nodes": nodes, "edges": edges}
                self.view.scene().load_scene(online=True, data=scene_data)
                self.status.setText(f"Online: Room {self.token} (v{version})")
            else:
                changes = data.get('changes', {})
                version = data.get('version', 0)
                self.view.scene().apply_delta(changes)
                self.status.setText(f"Online: Room {self.token} (v{version})")
        except Exception as esd:
            print(esd)
    
    def on_user_joined(self, data):
        user = data.get('user_info', {}).get('name', 'Unknown')
        total = data.get('total_clients', 0)
        self.status.setText(f"User '{user}' joined (Total: {total})")
    
    def on_user_left(self, data):
        user = data.get('user_info', {}).get('name', 'Unknown')
        self.status.setText(f"User '{user}' left")
    
    def on_error(self, error):
        print(f"Error: {error}")
        QMessageBox.warning(self, "Collaboration Error", error)
        self.status.setText("Error occurred")
    
    def closeEvent(self, event):
        self.client.disconnect()
        event.accept()