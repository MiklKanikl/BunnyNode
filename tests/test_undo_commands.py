from PyQt6.QtCore import QPointF, QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QColor, QImage

from editor.items.rectangle import NodeRect
from tests.conftest import actual_scene_items


def test_add_and_delete_commands_undo_and_redo(scene, controller):
    node = NodeRect(10, 20, 50, 40, QColor("red"))

    controller.add_node(scene, node)
    assert node in scene.items()
    controller.undo_action()
    assert node not in scene.items()
    controller.redo_action()
    assert node in scene.items()

    controller.delete_node(scene, [node])
    assert node not in scene.items()
    controller.undo_action()
    assert node in scene.items()
    controller.redo_action()
    assert node not in scene.items()

def test_delete_edge_command_undo_and_redo(scene, controller, added_item_pack):
    edge = added_item_pack[3]

    controller.delete_node(scene, [edge])
    assert edge not in scene.items()
    controller.undo_action()
    assert edge in scene.items()
    controller.redo_action()
    assert edge not in scene.items()


def test_move_and_rename_commands_undo_and_redo(
    scene, controller, added_item_pack
):
    node = added_item_pack[0]
    original_pos = node.pos()
    moved_pos = QPointF(25, 35)

    controller.move_node([node], [original_pos], [moved_pos])
    assert node.pos() == moved_pos
    controller.undo_action()
    assert node.pos() == original_pos
    controller.redo_action()
    assert node.pos() == moved_pos

    controller.rename_node(node, node.text, "renamed")
    assert node.text == "renamed"
    assert node.label.toPlainText() == "renamed"
    controller.undo_action()
    assert node.text == ""
    assert node.label.toPlainText() == ""
    controller.redo_action()
    assert node.text == "renamed"
    assert node.label.toPlainText() == "renamed"


def test_node_property_commands_undo_and_redo(
    scene, controller, added_item_pack
):
    node = added_item_pack[0]

    old_color = QColor(node.color)
    new_color = QColor("green")
    controller.change_color(node, old_color, new_color)
    assert node.color == new_color
    controller.undo_action()
    assert node.color == old_color
    controller.redo_action()
    assert node.color == new_color

    old_text_color = QColor(node.text_color)
    new_text_color = QColor("blue")
    controller.change_text_color(node, old_text_color, new_text_color)
    assert node.text_color == new_text_color
    controller.undo_action()
    assert node.text_color == old_text_color
    controller.redo_action()
    assert node.text_color == new_text_color

    old_size = (node.width, node.height)
    controller.resize_node(node, node.width, node.height, 200, 120)
    assert (node.width, node.height) == (200, 120)
    controller.undo_action()
    assert (node.width, node.height) == old_size
    controller.redo_action()
    assert (node.width, node.height) == (200, 120)

    old_z_value = node.zValue()
    controller.change_z_order(node, to_front=True)
    new_z_value = node.zValue()
    assert new_z_value > old_z_value
    controller.undo_action()
    assert node.zValue() == old_z_value
    controller.redo_action()
    assert node.zValue() == new_z_value


def test_edge_property_and_reconnect_commands_undo_and_redo(
    scene, controller, added_item_pack
):
    edge = added_item_pack[3]
    original_text = edge.text
    controller.rename_edge(edge, original_text, "edge label")
    assert edge.text == "edge label"
    controller.undo_action()
    assert edge.text == original_text
    controller.redo_action()
    assert edge.text == "edge label"

    old_end = edge.end_node
    new_end = added_item_pack[2]
    controller.reconnect_edge(edge, "end", new_end)
    assert edge.end_node is new_end
    controller.undo_action()
    assert edge.end_node is old_end
    controller.redo_action()
    assert edge.end_node is new_end

    old_color = QColor(edge.color)
    new_color = QColor("green")
    controller.change_color(edge, old_color, new_color)
    assert edge.color == new_color
    controller.undo_action()
    assert edge.color == old_color
    controller.redo_action()
    assert edge.color == new_color

    old_text_color = QColor(edge.text_color)
    new_text_color = QColor("blue")
    controller.change_text_color(edge, old_text_color, new_text_color)
    assert edge.text_color == new_text_color
    controller.undo_action()
    assert edge.text_color == old_text_color
    controller.redo_action()
    assert edge.text_color == new_text_color

    old_width = edge.p_width
    controller.resize_edge(edge, old_width, 10)
    assert edge.p_width == 10
    controller.undo_action()
    assert edge.p_width == old_width
    controller.redo_action()
    assert edge.p_width == 10

    old_weight = edge.weight
    controller.change_weight(edge, old_weight, old_weight + 3)
    assert edge.weight == old_weight + 3
    controller.undo_action()
    assert edge.weight == old_weight
    controller.redo_action()
    assert edge.weight == old_weight + 3

    old_z_value = edge.zValue()
    controller.change_z_order(edge, to_front=True)
    new_z_value = edge.zValue()
    assert new_z_value > old_z_value
    controller.undo_action()
    assert edge.zValue() == old_z_value
    controller.redo_action()
    assert edge.zValue() == new_z_value


def test_paste_command_undo_and_redo(scene, controller, added_item_pack):
    rect, ellipse, _image, edge, _directed_edge = added_item_pack
    original_count = len(actual_scene_items(scene))
    controller.clipboard.copy([rect, ellipse, edge])

    controller.paste(scene)
    assert len(actual_scene_items(scene)) == original_count + 3
    controller.undo_action()
    assert len(actual_scene_items(scene)) == original_count
    controller.redo_action()
    assert len(actual_scene_items(scene)) == original_count + 3


def test_load_image_command_undo_and_redo(
    scene, controller, added_item_pack
):
    image_node = added_item_pack[2]
    image = QImage(2, 2, QImage.Format.Format_ARGB32)
    image.fill(QColor("red"))
    buffer_data = QByteArray()
    buffer = QBuffer(buffer_data)
    assert buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "PNG")
    buffer.close()
    new_image_data = buffer_data.toBase64().data().decode("ascii")
    old_image_data = image_node.img_data

    controller.load_image(
        image_node,
        image_node.width,
        image_node.height,
        old_image_data,
        new_image_data,
    )
    assert image_node.img_data == new_image_data
    controller.undo_action()
    assert image_node.img_data == old_image_data
    controller.redo_action()
    assert image_node.img_data == new_image_data
