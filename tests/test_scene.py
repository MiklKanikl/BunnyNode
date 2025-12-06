def test_def_item_pack(scene, default_item_pack):
    for item in default_item_pack:
        scene.addItem(item)
    assert len(scene.items()) == 5