import json

from PyQt6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from editor.path_utils import get_settings_path

class Settings_menu(QWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)
        self.setObjectName("settingsMenu")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        settings_layout = QFormLayout()
        settings_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light", "light")
        self.theme_combo.addItem("Dark", "dark")
        settings_layout.addRow("Theme:", self.theme_combo)
        layout.addLayout(settings_layout)
        
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
        
        layout.addStretch()
        self.setLayout(layout)
        self.load_settings()
    
    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(140, 32)
        button.clicked.connect(callback)
        return button

    def load_settings(self):
        settings = self.parent.controller.get_current_settings()
        theme = settings.get("theme", "dark")
        index = self.theme_combo.findData(theme)
        self.theme_combo.setCurrentIndex(index if index >= 0 else 0)
    
    def back_to_editor(self):
        self.parent.stacked_widget.setCurrentWidget(self.parent.view)
        self.parent.show_bars()
    
    def apply_settings(self):
        settings = self.parent.controller.get_current_settings()
        theme = self.theme_combo.currentData()
        settings["theme"] = theme
        settings_path = get_settings_path()
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)
        self.parent.apply_theme(theme)
        self.parent.view.update_settings_stats()
    
    def reset_settings(self):
        self.theme_combo.setCurrentIndex(self.theme_combo.findData("dark"))
        self.apply_settings()