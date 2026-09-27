import threading
import asyncio

from PyQt6.QtGui import QColor

from editor.client.client import Client
from editor.items.node import NodeRect
from editor.core.scene import DiagramScene


def test_join_room_does_not_request_full_state_until_ack_is_received():
    client = Client(server_url="http://127.0.0.1:5000")
    client._connect_websocket = lambda: True
    client._awaiting_initial_state = True

    seen = []

    def fake_request_full_state():
        seen.append(True)

    client.request_full_state = fake_request_full_state

    client.join_room(123)
    assert client._awaiting_initial_state is True
    assert seen == []

    async def run():
        await client._handle_message('{"type": "joined", "session_id": "abc", "version": 7, "room": 123}')

    asyncio.run(run())
    assert client._awaiting_initial_state is False
    assert seen == [True]


def test_scene_update_ignores_stale_version():
    client = Client(server_url="http://127.0.0.1:5000")
    client.current_version = 8
    client.scene_updated = lambda *args, **kwargs: None

    async def run():
        await client._handle_message('{"type": "scene_update", "version": 7, "changes": {"type": "nodes_added"}}')

    asyncio.run(run())
    assert client.current_version == 8


def test_remote_node_rename_updates_text_and_label(qapp):
    scene = DiagramScene()
    node = NodeRect(10, 20, 50, 40, QColor(255, 0, 0), text="old")
    scene.addItem(node)

    scene.apply_delta({
        "type": "nodes_modified",
        "nodes": [{"id": node.id, "text": "new name"}],
    })

    assert node.text == "new name"
    assert node.label.toPlainText() == "new name"


def test_node_classes_are_exposed_from_node_module():
    from editor.items import node as node_module

    assert hasattr(node_module, "NodeRect")
    assert hasattr(node_module, "NodeEllipse")
