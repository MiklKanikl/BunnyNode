from PyQt6.QtGui import QColor

from editor.items.node import NodeItem
from editor.items.edge import EdgeItem
from tests.conftest import actual_scene_items

def test_remove_item(scene, controller, added_item_pack):
    initial_count = len(actual_scene_items(scene))
    item_to_remove = added_item_pack[0]
    controller.delete_node(scene, [item_to_remove])
    assert len(actual_scene_items(scene)) == initial_count - 1
    assert item_to_remove not in actual_scene_items(scene)

def test_change_node_color(scene, controller, added_item_pack):
    node = added_item_pack[0]
    old_color = node.color
    new_color = QColor(0, 255, 0)
    controller.change_color(node, old_color, new_color)
    assert node.color != old_color
    assert node.color == new_color

def test_remove_edges(scene, controller, added_item_pack):
    initial_count = len(actual_scene_items(scene))
    edge_to_remove = added_item_pack[3]
    controller.delete_node(scene, [edge_to_remove])
    assert len(actual_scene_items(scene)) == initial_count - 1
    assert edge_to_remove not in actual_scene_items(scene)

def test_node_resize_updates_size_and_edge_positions(scene, controller, added_item_pack):
    node = added_item_pack[0]
    edge = added_item_pack[3]
    old_start = edge.path().pointAtPercent(0)

    controller.resize_node(node, node.width, node.height, 200, 200)

    assert node.width == 200
    assert node.height == 200
    assert edge.path().pointAtPercent(0) != old_start

def test_image_node_image_load_and_resize(scene, controller, added_item_pack):
    image_node = added_item_pack[2]
    old_width = image_node.width
    old_height = image_node.height

    controller.resize_node(image_node, old_width, old_height, 300, 150)

    assert image_node.width == 300
    assert image_node.height == 150