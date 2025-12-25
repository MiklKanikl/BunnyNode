from pathlib import Path

BASE = Path(__file__).parent
ICON_DIR = BASE / "resources" / "icons"

def icon(name: str):
    return str(ICON_DIR / name)