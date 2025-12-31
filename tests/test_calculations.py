from editor.items.node import NodeRect, NodeEllipse
from editor.calculations.dijkstra import shortest_path

def test_dijkstra_shortest_path(scene, default_item_pack):
    for item in default_item_pack:
        scene.addItem(item)
    assert len(scene.items()) == 5
    nodes = [item for item in scene.items() if isinstance(item, NodeRect) or isinstance(item, NodeEllipse)]
    a = nodes[0]
    b = nodes[1]
    g = scene.weighted_graph()
    d, prev = shortest_path(g, a, b)
    assert d is not None
    assert isinstance(d, (int, float))