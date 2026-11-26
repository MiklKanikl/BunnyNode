from editor.items.node import NodeItem
from editor.items.edge import EdgeItem

def test_save_load_default_itempack(scene, added_item_pack, save_dir):
    assert sum(isinstance(item, NodeItem) for item in scene.items()) == 3
    assert sum(isinstance(item, EdgeItem) for item in scene.items()) == 2
    save_path = save_dir / "test_save_load_default_itempack.diagram"
    scene.save_scene(str(save_path))
    scene.clear()
    assert len(scene.items()) == 0
    scene.load_scene(str(save_path))
    assert sum(isinstance(item, NodeItem) for item in scene.items()) == 3
    assert sum(isinstance(item, EdgeItem) for item in scene.items()) == 2

def test_save_load_empty_scene(scene, save_dir):
    save_path = save_dir / "test_save_load_empty.diagram"
    scene.save_scene(str(save_path))
    scene.clear()
    assert len(scene.items()) == 0
    scene.load_scene(str(save_path))
    assert len(scene.items()) == 0

def test_save_load_preserves_node_and_edge_properties(
    scene, controller, added_item_pack, save_dir
):
    node = added_item_pack[0]
    edge = added_item_pack[3]
    controller.resize_node(node, node.width, node.height, 150, 90)
    controller.rename_edge(edge, edge.text, "from-a-to-b")
    controller.resize_edge(edge, edge.p_width, 10)
    controller.change_weight(edge, edge.weight, 6)
    save_path = save_dir / "properties.diagram"

    scene.save_scene(str(save_path))
    scene.clear()
    scene.load_scene(str(save_path))

    loaded_node = next(item for item in scene.items() if isinstance(item, type(node)))
    loaded_edge = next(
        item for item in scene.items()
        if hasattr(item, "directed") and not item.directed
    )
    assert loaded_node.width == 150
    assert loaded_node.height == 90
    assert loaded_edge.text == "from-a-to-b"
    assert loaded_edge.p_width == 10
    assert loaded_edge.weight == 6