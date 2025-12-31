def test_png_export_default_itempack(scene, default_item_pack, export_dir):
    for item in default_item_pack:
        scene.addItem(item)
    path = export_dir / "export.png"
    scene.export_png(str(path))
    assert path.exists()
    assert path.stat().st_size > 0

def test_png_export_empty_scene(scene, export_dir):
    path = export_dir / "export_empty.png"
    scene.export_png(str(path))
    assert path.exists()
    assert path.stat().st_size > 0