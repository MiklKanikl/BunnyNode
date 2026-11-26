from PyQt6.QtGui import QColor

from editor.items.ellipse import NodeEllipse
from editor.items.rectangle import NodeRect
from editor.calculations.dijkstra import shortest_path
from editor.items.edge import EdgeItem

def test_dijkstra_shortest_path(scene, added_item_pack):
    assert sum(isinstance(item, NodeRect) or isinstance(item, NodeEllipse)
               for item in scene.items()) == 2
    nodes = [
        item for item in scene.items()
        if isinstance(item, (NodeRect, NodeEllipse))
    ]
    a, b = nodes
    g = scene.weighted_graph()
    d, prev = shortest_path(g, a, b)
    edge = next(
        item for item in added_item_pack
        if isinstance(item, EdgeItem) and not item.directed
    )
    assert d is not None
    assert d == edge.laenge()

def test_dijkstra_returns_no_path_for_disconnected_nodes(scene, controller):
    a = NodeRect(0, 0, 40, 40, QColor(255, 0, 0))
    b = NodeEllipse(500, 500, 40, 40, QColor(255, 0, 0))
    controller.add_node(scene, a)
    controller.add_node(scene, b)

    distance, previous = shortest_path(scene.weighted_graph(), a, b)

    assert distance is None
    assert previous == {}

def test_graphs_respect_directed_and_custom_weights(scene, controller, added_item_pack):
    rect, ellipse, _image, undirected, directed = added_item_pack
    controller.change_weight(undirected, undirected.weight, 4)
    controller.change_weight(directed, directed.weight, 7)

    custom = scene.custom_weighted_graph()
    unweighted = scene.unweighted_graph()

    assert [neighbor for neighbor, weight in custom[rect]
            if neighbor is ellipse] == [ellipse]
    assert next(weight for neighbor, weight in custom[rect] if neighbor is ellipse) == 4
    assert next(weight for neighbor, weight in custom[ellipse] if neighbor is directed.end_node) == 7
    assert custom[directed.end_node] == []
    assert all(weight == 1 for _, weight in unweighted[rect])