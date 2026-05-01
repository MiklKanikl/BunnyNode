from PyQt6.QtWidgets import QApplication, QGraphicsView
from editor.core.scene import DiagramScene
from editor.ui.view import DiagramView
from editor.core.main_window import EditorWindow

import sys

def main():
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
    main()