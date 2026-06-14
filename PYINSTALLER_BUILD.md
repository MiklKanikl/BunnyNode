# PyInstaller Build Guide for BunnyNode

## Overview

This guide explains how to build BunnyNode Diagram Editor as a standalone Windows executable using PyInstaller.

## Prerequisites

1. **Python 3.8+** installed
2. **All dependencies** from requirements.txt installed
3. **PyInstaller** installed

### Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Building the Application

### Quick Build (Recommended)

Run the automated build script:

```bash
python build.py
```

This will:
- Clean previous builds
- Compile the application
- Create `dist/BunnyNode/` directory with the executable
- Verify the build succeeded

### Manual Build with PyInstaller

If you prefer manual control, use:

```bash
pyinstaller --onedir ^
  --windowed ^
  --name BunnyNode ^
  --icon=editor/resources/icons/window.png ^
  --add-data=editor/resources:editor/resources ^
  --add-data=editor/recent_files.json:editor ^
  --add-data=editor/default_settings.json:editor ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  main.py
```

## Data Directory Handling

When running the compiled executable, the application automatically:

1. **Creates a data directory** at: `%USERPROFILE%/.bunnynode/`
2. **Stores saves** in: `%USERPROFILE%/.bunnynode/saves/`
3. **Stores exports** in: `%USERPROFILE%/.bunnynode/exports/`
4. **Stores settings** in: `%USERPROFILE%/.bunnynode/your_settings.json`

### Why This Approach?

- **Portable**: The executable doesn't need to be in a specific directory
- **User-friendly**: Data is stored in the user's home directory, not in Program Files
- **Multiple instances**: Each user can have their own data directory
- **Development friendly**: When running as a script, uses project root for backward compatibility

## Running the Application

### After Building

```bash
# Option 1: Run directly
dist/BunnyNode/BunnyNode.exe

# Option 2: Create a shortcut
# Right-click BunnyNode.exe → Create shortcut
# Move shortcut to Desktop or Start Menu
```

### Check Build Contents

The compiled application includes:
- PyQt6 libraries
- All Python dependencies
- Resource files (icons, images)
- Recent files configuration
- Default settings

## Troubleshooting

### Issue: "Failed to execute script"

**Solution**: Ensure all required dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Icons not showing in compiled version

**Solution**: The `--add-data` flags in build.py ensure resources are included. If icons still don't show, verify:
1. Icon files exist in `editor/resources/icons/`
2. Recent_files.json exists in `editor/`
3. The build.py script was used (includes all data paths)

### Issue: Saves/exports directory issues

**Solution**: The application creates these directories automatically:
1. On first run, it creates `%USERPROFILE%/.bunnynode/`
2. Saves go to the `saves/` subdirectory
3. Exports go to the `exports/` subdirectory

No manual creation needed - the application handles this automatically.

## Distribution

To distribute BunnyNode:

1. **Single Directory Distribution**: Zip the entire `dist/BunnyNode/` folder
2. **Create Installer**: Use NSIS, Inno Setup, or similar to wrap the executable
3. **Single File**: Use `--onefile` flag (slower startup, larger size) instead of `--onedir`

### For a Single .exe File

```bash
pyinstaller --onefile ^
  --windowed ^
  --name BunnyNode ^
  --icon=editor/resources/icons/window.png ^
  --add-data=editor/resources:editor/resources ^
  --add-data=editor/recent_files.json:editor ^
  --add-data=editor/default_settings.json:editor ^
  --hidden-import=PyQt6.QtCore ^
  --hidden-import=PyQt6.QtGui ^
  --hidden-import=PyQt6.QtWidgets ^
  main.py
```

## Notes

- **Build time**: First build takes 30-60 seconds depending on system
- **File size**: Executable is ~250-350MB (PyQt6 is large)
- **Performance**: Compiled version runs at same speed as Python script
- **Updates**: Simply replace the `.exe` and dependencies to update

## Development vs. Production

The application automatically detects whether it's running as:
- **Script**: Data stored in project root (for development)
- **Executable**: Data stored in `%USERPROFILE%/.bunnynode/` (for end users)

This is handled automatically by the `path_utils.py` module.
