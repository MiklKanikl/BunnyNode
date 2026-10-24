import os

from PyQt6.QtWidgets import QInputDialog, QMainWindow, QMessageBox, QStatusBar, QLabel, QStackedWidget, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from editor.resources import icon
from editor.ui.welcomescreen import WelcomeScreen
from editor.ui.settings_menu import Settings_menu
from editor.ui.components.inspectordock import InspectorDock
from editor.ui.components.calcdock import CalcDock
from editor.ui.components.createdock import Createdock
from editor.ui.components.dock_tabs_container import DockTabsContainer
from editor.controller.app_controller import AppController
from editor.client.client import Client

class EditorWindow(QMainWindow):
    def __init__(self, view):
        super().__init__()
        self.setWindowTitle("BunnyNode")
        self.setWindowIcon(QIcon(icon("window.png")))
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.view = view
        self.welcome_screen = WelcomeScreen(self)
        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(view)
        self.controller = AppController()
        self.view.scene().update_recent_files()
        self.settings_menu = Settings_menu(self)
        self.stacked_widget.addWidget(self.settings_menu)
        self.build_menubar()
        self.online = False
        self.view.scene().save_file_changed.connect(self.update_filename_label)
        self.controller.undostack.cleanChanged.connect(
            lambda _clean: self.update_filename_label(self.view.scene().auto_save_file)
        )
        self.update_filename_label(self.view.scene().auto_save_file)
        self.build_toolbar()
        self.build_statusbar()
        self.create_docks()
        self.hide_bars()
        self.view.scene().set_online_mode(False)
        self.token = None
        self.client = Client()
        self.client.connection_ready.connect(self.on_connection_ready)
        self.client.room_joined.connect(self.on_room_joined)
        self.client.scene_updated.connect(self.on_scene_updated)
        self.client.user_joined.connect(self.on_user_joined)
        self.client.user_left.connect(self.on_user_left)
        self.client.error_occurred.connect(self.on_error)
        self.client.undo_last_command.connect(lambda: self.controller.undostack.undo())
        self.apply_theme(self.controller.get_current_settings().get("theme", "dark"))
        self.client.start()

    def apply_theme(self, theme):
        themes = {
            "light": {
                "window": "#f4f6f8",
                "surface": "#ffffff",
                "text": "#20252b",
                "border": "#c8ced6",
                "button": "#e4e8ed",
                "button_hover": "#d6dce3",
                "selection": "#c7dcf3",
            },
            "dark": {
                "window": "#20252b",
                "surface": "#2b3139",
                "text": "#e8edf2",
                "border": "#48515c",
                "button": "#3a424c",
                "button_hover": "#48525e",
                "selection": "#465d77",
            },
        }
        colors = themes.get(theme, themes["light"])
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {colors["window"]};
                color: {colors["text"]};
            }}
            QLabel {{
                background-color: transparent;
                color: {colors["text"]};
            }}
            QGraphicsView {{
                background-color: #ffffff;
                color: #000000;
            }}
            QPushButton {{
                background-color: {colors["button"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 6px;
                padding: 5px 9px;
            }}
            QPushButton:hover {{
                background-color: {colors["button_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {colors["border"]};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QListWidget {{
                background-color: {colors["surface"]};
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 3px;
                padding: 3px;
                selection-background-color: {colors["selection"]};
            }}
            QGroupBox {{
                color: {colors["text"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }}
            QMenuBar, QMenu, QToolBar, QStatusBar, QDockWidget {{
                background-color: {colors["surface"]};
                color: {colors["text"]};
            }}
            QMenu::item:selected {{
                background-color: {colors["selection"]};
            }}
            QDockWidget::title {{
                background-color: {colors["surface"]};
                color: {colors["text"]};
                padding: 5px;
            }}
            QScrollArea {{
                background-color: {colors["window"]};
                border: 1px solid {colors["border"]};
            }}
            QScrollArea QWidget {{
                background-color: {colors["window"]};
            }}
        """)
    
    def build_statusbar(self):
        self.setStatusBar(QStatusBar(self))
        self.status = QLabel("idle")
        self.statusBar().addPermanentWidget(self.status)

    def build_toolbar(self):
        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        undo_action.triggered.connect(self.controller.undo_action)
        redo_action.triggered.connect(self.controller.redo_action)
        undo_action.setEnabled(self.controller.undostack.canUndo())
        redo_action.setEnabled(self.controller.undostack.canRedo())
        self.controller.undostack.canUndoChanged.connect(undo_action.setEnabled)
        self.controller.undostack.canRedoChanged.connect(redo_action.setEnabled)
        undo_action.setIcon(QIcon(icon("undo.png")))
        redo_action.setIcon(QIcon(icon("redo.png")))
        undo_action.setShortcut("Ctrl+Z")
        redo_action.setShortcut("Ctrl+Y")
        self.toolbar = self.addToolBar("Edit")
        self.toolbar.addAction(undo_action)
        self.toolbar.addAction(redo_action)
    
    def build_menubar(self):
        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("&File")
        actions_menu = self.menu.addMenu("&Actions")
        calc_menu = self.menu.addMenu("&Calc")
        other_menu = self.menu.addMenu("&Other")

        self.create_filname_label()

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

        save_as = QAction(QIcon(icon("save.png")), "Save As", self)
        file_menu.addAction(save_as)
        save_as.triggered.connect(self.view.save_diagram_as)

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
        dist.triggered.connect(lambda: self.view.compute_distance(unweighted=False))

        dist_unweighted = QAction(QIcon(icon("distance.png")), "Distance Unweighted", self)
        calc_menu.addAction(dist_unweighted)
        dist_unweighted.triggered.connect(lambda: self.view.compute_distance(unweighted=True))

        settings = QAction(QIcon(icon("settings.png")), "Settings", self)
        other_menu.addAction(settings)
        settings.triggered.connect(self.open_settings)

    def create_filname_label(self):
        self.filename_label = QLabel()
        self.filename_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.filename_label.setContentsMargins(0, 8, 12, 0)
        self.menu.setCornerWidget(self.filename_label, Qt.Corner.TopRightCorner)

    def delete_filename_label(self):
        if hasattr(self, 'filename_label'):
            self.menu.setCornerWidget(None, Qt.Corner.TopRightCorner)
            self.filename_label.deleteLater()
            self.filename_label = None

    def update_filename_label(self, filename):
        scene = self.view.scene()
        if self.online:
            label = f"Room {self.token}" if self.token is not None else ""
            tooltip = f"Room token: {self.token}" if self.token is not None else ""
        else:
            label = os.path.basename(filename) if filename else ""
            tooltip = filename
            if scene.has_unsaved_changes():
                label += "*"
                if not filename:
                    tooltip = "Unsaved diagram"

        self.delete_filename_label()
        self.create_filname_label()
        self.filename_label.setText(label)
        self.filename_label.setToolTip(tooltip)
        self.filename_label.setVisible(bool(label))
    
    def exit_popup(self, action):
        if self.view.scene().has_unsaved_changes():
            popup = QMessageBox()
            popup.setWindowTitle("Warning")
            text = "You have unsaved changes. Do you want to save them before proceeding?"
            popup.setText(text)
            popup.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if popup.exec() == QMessageBox.StandardButton.Yes:
                self.view.save_diagram()
                if action == 0:
                    self.new_diagram()
                elif action == 1:
                    self.back_to_welcome()
            elif popup.exec() == QMessageBox.StandardButton.No:
                if action == 0:
                    self.new_diagram()
                elif action == 1:
                    self.back_to_welcome()
            else:
                pass
        else:
            if action == 0:
                self.new_diagram()
            elif action == 1:
                self.back_to_welcome()
    
    def create_docks(self):
        self.calcdock = CalcDock("Calc results", self)
        self.inspectordock = InspectorDock("Inspector", self)
        self.createdock = Createdock(self)
        self.dock_tabs_container = DockTabsContainer(self)

        self.calcdock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        self.inspectordock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.createdock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.calcdock)
        self.dock_tabs_container.add_tab(
            self.inspectordock, Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.dock_tabs_container.add_tab(
            self.createdock, Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.inspectordock.raise_()
    
    def back_to_welcome(self):
        self.view.scene().update_recent_files()
        self.online = False
        self.token = None
        self.view.scene().set_online_mode(False)
        self.view.scene().clear()
        self.view.scene().controller.clear_history()
        self.stacked_widget.setCurrentWidget(self.welcome_screen)
        self.hide_bars()
        self.welcome_screen.reload_recent_files()
        self.client.leave_room()
        self.update_filename_label(self.view.scene().auto_save_file)
    
    def open_settings(self):
        self.settings_menu.load_settings()
        self.stacked_widget.setCurrentWidget(self.settings_menu)
        self.hide_bars()
    
    def new_diagram(self):
        self.view.scene().clear()
        self.controller.clear_history()
        self.stacked_widget.setCurrentWidget(self.view)
        self.show_bars()
    
    def open_diagram(self):
        self.stacked_widget.setCurrentWidget(self.view)
        self.view.load_a_diagram(False)
        self.show_bars()
    
    def create_room(self):
        if self.client.create_room():
            self.token = self.client.room_id
            self.online = False
            self.view.scene().set_online_mode(False)
            self.stacked_widget.setCurrentWidget(self.view)
            self.show_bars()
            self.status.setText(f"Connecting to room {self.token}...")
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
        self.createdock.show()
        self.menu.show()
        self.toolbar.show()
        self.statusBar().show()
    
    def hide_bars(self):
        self.calcdock.dist_label.setText("Waiting for Computation...")
        self.calcdock.hide()
        self.inspectordock.hide()
        self.createdock.hide()
        self.menu.hide()
        self.toolbar.hide()
        self.statusBar().hide()
    
    def on_connection_ready(self, ready):
        if ready:
            if self.token and not self.online:
                self.status.setText(f"Connecting to room {self.token}...")
            else:
                self.status.setText("Connection ready")
        else:
            self.online = False
            self.view.scene().set_online_mode(False)
            self.status.setText("Connection lost")
        self.update_filename_label(self.view.scene().auto_save_file)
    
    def on_room_joined(self, data):
        self.token = data.get('room')
        self.online = True
        self.view.scene().set_online_mode(True)
        version = data.get('version', 0)
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        scene_data = {"nodes": nodes, "edges": edges}
        self.view.scene().load_scene(online=True, data=scene_data)
        self.stacked_widget.setCurrentWidget(self.view)
        self.show_bars()
        self.status.setText(f"Online: Room {self.token} (v{version})")
        self.update_filename_label(self.view.scene().auto_save_file)
    
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
        if self.view.scene().has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before proceeding?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.view.save_diagram()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        self.client.disconnect()
        event.accept()