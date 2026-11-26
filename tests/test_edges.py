from editor.items.edge import EdgeItem
from tests.conftest import actual_scene_items

def test_remove_edge(scene, controller, added_item_pack):
    initial_count = len(actual_scene_items(scene))
    edge_to_remove = added_item_pack[3]
    controller.delete_node(scene, [edge_to_remove])
    assert len(actual_scene_items(scene)) == initial_count - 1
    assert edge_to_remove not in actual_scene_items(scene)

def test_edge_endpoint_can_be_reconnected(scene, controller, added_item_pack):
    edge = added_item_pack[3]
    old_end = edge.end_node
    new_end = added_item_pack[2]

    controller.reconnect_edge(edge, "end", new_end)

    assert edge.end_node is new_end
    assert edge not in old_end.edges
    assert edge in new_end.edges

def test_edge_weight_change(scene, controller, added_item_pack):
    edge = added_item_pack[3]
    old_weight = edge.weight
    new_weight = 5

    controller.change_weight(edge, old_weight, new_weight)

    assert edge.weight == new_weight

def test_edge_rename(scene, controller, added_item_pack):
    edge = added_item_pack[3]
    old_text = edge.text
    new_text = "new label"

    controller.rename_edge(edge, old_text, new_text)

    assert edge.text == new_text

def test_edge_resize(scene, controller, added_item_pack):
    edge = added_item_pack[3]
    old_width = edge.p_width
    new_width = 10

    controller.resize_edge(edge, old_width, new_width)

    assert edge.p_width == new_width