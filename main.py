from PyQt6.QtWidgets import QApplication, QGraphicsView
from editor.core.scene import DiagramScene
from editor.core.view import DiagramView
from editor.core.window import EditorWindow

import sys

def main():
    app = QApplication(sys.argv)

    scene = DiagramScene()

    view = DiagramView(scene)
    view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
    
    win = EditorWindow(view)
    win.showMaximized()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()