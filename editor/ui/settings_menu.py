from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSpinBox, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from editor.path_utils import get_settings_path

class Settings_menu(QWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        layout.addSpacing(10)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = self.create_button("Apply Settings", self.apply_settings)
        button_layout.addWidget(self.apply_button)

        self.reset_button = self.create_button("Reset to Default", self.reset_settings)
        button_layout.addWidget(self.reset_button)

        self.back_button = self.create_button("Back to Editor", self.back_to_editor)
        button_layout.addWidget(self.back_button)
        
        layout.addLayout(button_layout)
        layout.addSpacing(30)

        self.in_progress_label = QLabel("Settings coming soon...")
        self.in_progress_label.setStyleSheet("font-size: 36px; color: white;")
        self.in_progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.in_progress_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(120, 32)
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #293847;
            }
            QPushButton:pressed {
                background-color: #1c2833;
            }
        """)
        return button
    
    def back_to_editor(self):
        self.parent.stacked_widget.setCurrentWidget(self.parent.view)
        self.parent.show_bars()
    
    def apply_settings(self):
        settings = {}
        import json
        settings_path = get_settings_path()
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
        self.parent.view.scene().controller.get_current_settings()
        self.parent.view.update_settings_stats()
    
    def reset_settings(self):
        pass