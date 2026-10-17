from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QImage


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


def test_png_export_selected_region_uses_only_region_bounds(scene, default_item_pack, export_dir):
    for item in default_item_pack:
        scene.addItem(item)

    path = export_dir / "export_region.png"
    scene.export_png(str(path), QRectF(310, 310, 50, 30))

    image = QImage(str(path))
    assert image.width() == 50
    assert image.height() == 30
    assert image.pixelColor(25, 15) == QColor(255, 0, 0)