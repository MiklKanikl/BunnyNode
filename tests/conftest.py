import sys
import pytest
import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor
from editor.core.scene import DiagramScene
from editor.controller.app_controller import AppController
from editor.items.directed_edge import DirectedEdgeItem
from editor.items.image import ImageNode
from editor.ui.view import DiagramView
from editor.items.ellipse import NodeEllipse
from editor.items.rectangle import NodeRect
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

def actual_scene_items(scene):
    actual_items = []
    for item in scene.items():
        if isinstance(item, (NodeRect, NodeEllipse, ImageNode, EdgeItem, DirectedEdgeItem)):
            actual_items.append(item)
    return actual_items

@pytest.fixture
def controller(scene):
    app_controller = AppController()
    app_controller.scene = scene
    app_controller.win = SimpleNamespace(online=False)
    scene.controller = app_controller
    yield app_controller
    app_controller.clear_history()

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
    n3 = ImageNode(410, 400, 100, 100, QColor(255, 0, 0), "", [])
    e1 = EdgeItem(n1, n2)
    e2 = DirectedEdgeItem(n2, n3)
    return n1, n2, n3, e1, e2

@pytest.fixture
def added_item_pack(scene, controller, default_item_pack):
    for item in default_item_pack:
        controller.add_node(scene, item)
    return default_item_pack

@pytest.fixture
def save_dir(tmp_path):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    return save_dir

@pytest.fixture
def export_dir(tmp_path):
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    return export_dir