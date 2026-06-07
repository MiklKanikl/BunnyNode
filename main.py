from PyQt6.QtWidgets import QApplication, QGraphicsView
from editor.core.scene import DiagramScene
from editor.ui.view import DiagramView
from editor.core.main_window import EditorWindow
from editor.path_utils import get_application_path

import sys
import os

def main():
    # Ensure proper working directory for resources
    app_path = get_application_path()
    
    app = QApplication(sys.argv)

    scene = DiagramScene()

    view = DiagramView(scene)
    view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
    
    win = EditorWindow(view)
    scene.set_services(win.controller)
    view.update_settings_stats()
    win.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    # Set working directory to project root when running as script
    if not getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()