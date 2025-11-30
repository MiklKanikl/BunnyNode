import pytest
from app.main import MainScene

def test_save_load():
    assert MainScene.save_scene is not None