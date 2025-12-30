def test_png_export(scene, default_item_pack, save_dir):
    for item in default_item_pack:
        scene.addItem(item)
    path = save_dir / "export.png"

    scene.export_png(path)
    assert path.exists()
    assert path.stat().st_size > 0