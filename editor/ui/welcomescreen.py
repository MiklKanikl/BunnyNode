from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QListWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from editor.resources import icon
from editor.path_utils import get_application_path
import os

class WelcomeScreen(QWidget):
    """Welcome Screen with quick access to common actions and recent files"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("BunnyNode")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        desc = QLabel("Create and manage your diagrams with ease. Start a new project or open an existing one.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        layout.addWidget(desc)
        
        layout.addSpacing(40)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        new_card = self.create_action_card(
            icon("new_diagram.png"), 
            "New Diagram", 
            "Create a new empty diagram", 
            self.new_diagram
        )
        grid.addWidget(new_card, 0, 0)
        
        open_card = self.create_action_card(
            icon("load.png"),
            "Open Diagram", 
            "Load an existing diagram from your files", 
            self.open_diagram
        )
        grid.addWidget(open_card, 0, 1)

        colab_card = self.create_action_card(
            icon("create_room.png"),
            "Create Colab room",
            "create a room for team collaboration",
            self.create_room
        )
        grid.addWidget(colab_card, 1, 0)

        colab_join_card = self.create_action_card(
            icon("join_room.png"),
            "Join Colab room",
            "join an existing collaboration room",
            self.join_room
        )
        grid.addWidget(colab_join_card, 1, 1)

        layout.addLayout(grid)
        
        layout.addSpacing(100)
        recent_label = QLabel("Recent Files:")
        recent_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(recent_label)
        
        self.recent_widget = QListWidget()
        self.recent_widget.setMaximumHeight(300)
        self.recent_widget.setMaximumWidth(600)
        self.recent_widget.itemDoubleClicked.connect(self.open_recent)
        layout.addWidget(self.recent_widget)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.load_recent_files()
    
    def create_action_card(self, iconn, title, description, callback):
        card = QPushButton()
        card.setFixedSize(200, 150)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(iconn).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        card.setLayout(layout)
        card.clicked.connect(callback)
        
        card.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                border: 2px solid dimgray;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #293847;
                border-color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #1c2833;
            }

        """)
        
        return card
    
    def new_diagram(self):
        self.parent.new_diagram()
    
    def open_diagram(self):
        self.parent.open_diagram()
    
    def create_room(self):
        self.parent.create_collaboration()
    
    def join_room(self):
        self.parent.join_collaboration()
    
    def open_recent(self, item):
        self.parent.open_recent_file(item.text())
    
    def load_recent_files(self):
        import json
        app_path = get_application_path()
        recent_files_path = os.path.join(app_path, "editor", "recent_files.json")
        
        try:
            with open(recent_files_path, "r") as f:
                recent_files = json.load(f)
            for file in recent_files:
                self.recent_widget.addItem(file)
        except FileNotFoundError:
            pass
    
    def reload_recent_files(self):
        self.recent_widget.clear()
        self.load_recent_files()