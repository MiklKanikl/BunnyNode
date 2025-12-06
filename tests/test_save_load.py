def test_save_load(scene, default_item_pack):
    for item in default_item_pack:
        scene.addItem(item)
    assert len(scene.items()) == 5
    scene.save_scene("test_save")
    for item in scene.items():
        scene.removeItem(item)
    assert len(scene.items()) == 0
    scene.load_scene("test_save")
    assert len(scene.items()) == 5