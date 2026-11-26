from editor.items.node import NodeItem
from editor.items.edge import EdgeItem

def test_def_item_pack(scene, added_item_pack):
    assert sum(isinstance(item, NodeItem) for item in scene.items()) == 3
    assert sum(isinstance(item, EdgeItem) for item in scene.items()) == 2

def test_empty_scene(scene):
    assert len(scene.items()) == 0