from PyQt6.QtGui import QColor

def test_remove_item(scene, default_item_pack):
    for item in default_item_pack:
        scene.addItem(item)
    initial_count = len(scene.items())
    item_to_remove = default_item_pack[0]
    scene.removeItem(item_to_remove)
    assert len(scene.items()) == initial_count - 2
    assert item_to_remove not in scene.items()

def test_change_node_color(scene, default_item_pack):
    for item in default_item_pack:
        scene.addItem(item)
    node = default_item_pack[0]
    old_color = node.color
    new_color = QColor(0, 255, 0)
    node.apply_color(new_color)
    assert node.color != old_color
    assert node.color == new_color

def test_remove_edges(scene, default_item_pack):
    for item in default_item_pack:
        scene.addItem(item)
    initial_count = len(scene.items())
    edge_to_remove = default_item_pack[2]
    for edge in default_item_pack[0].edges[:]:
        scene.removeItem(edge)
    assert len(scene.items()) == initial_count - 1
    assert edge_to_remove not in scene.items()