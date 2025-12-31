def test_save_load_default_itempack(scene, default_item_pack, save_dir):
    for item in default_item_pack:
        scene.addItem(item)
    assert len(scene.items()) == 5
    save_path = save_dir / "test_save_load_default_itempack.diagram"
    scene.save_scene(str(save_path))
    for item in scene.items():
        scene.removeItem(item)
    assert len(scene.items()) == 0
    scene.load_scene(str(save_path))
    assert len(scene.items()) == 5

def test_save_load_empty_scene(scene, save_dir):
    save_path = save_dir / "test_save_load_empty.diagram"
    scene.save_scene(str(save_path))
    for item in scene.items():
        scene.removeItem(item)
    assert len(scene.items()) == 0
    scene.load_scene(str(save_path))
    assert len(scene.items()) == 0