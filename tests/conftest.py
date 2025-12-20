import sys
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor
from editor.core.scene import DiagramScene
from editor.core.view import DiagramView
from editor.items.node import NodeEllipse, NodeRect
from editor.items.edge import EdgeItem

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def scene(qapp):
    s = DiagramScene()
    yield s
    s.clear()
    s.deleteLater()

@pytest.fixture
def view(scene):
    v = DiagramView(scene)
    v.setScene(scene)
    v.setDragMode(DiagramView.DragMode.RubberBandDrag)
    yield v
    v.close()
    v.deleteLater()

@pytest.fixture
def default_item_pack():
    n1 = NodeRect(300, 300, 140, 70, QColor(255, 0, 0))
    n2 = NodeEllipse(350, 350, 80, 80, QColor(255, 0, 0))
    e1 = EdgeItem(n1, n2)
    return n1, n2, e1

@pytest.fixture
def save_dir(tmp_path):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    return save_dir