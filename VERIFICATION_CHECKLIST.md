# PyInstaller Setup - Verification Checklist

## Pre-Build Checklist

Before building, verify everything is in place:

### ✅ Required Files Present
- [ ] `editor/path_utils.py` exists
- [ ] `build.py` exists
- [ ] `BunnyNode.spec` exists
- [ ] `main.py` is updated
- [ ] `requirements.txt` exists

### ✅ Code Updates
- [ ] `editor/core/scene.py` - Uses `get_saves_directory()`
- [ ] `editor/ui/view.py` - Uses `get_exports_directory()`
- [ ] `editor/ui/welcomescreen.py` - Uses `get_application_path()`
- [ ] `editor/ui/settings_menu.py` - Uses `get_settings_path()`
- [ ] `editor/controller/app_controller.py` - Uses `get_settings_path()`

### ✅ Resource Files
- [ ] `editor/resources/icons/window.png` exists
- [ ] `editor/recent_files.json` exists
- [ ] `editor/default_settings.json` exists
- [ ] All other icon files present in `editor/resources/`

### ✅ Dependencies
- [ ] PyQt6 installed: `pip list | grep PyQt6`
- [ ] PyInstaller installed: `pip install pyinstaller`
- [ ] All requirements from `requirements.txt` installed

### ✅ Development Test
- [ ] Application runs with `python main.py`
- [ ] Can create diagrams
- [ ] Can save diagrams (to `saves/`)
- [ ] Can load diagrams
- [ ] Can export as PNG (to `exports/`)
- [ ] No error messages in console

## Build Process

### Step 1: Verify Python Version
```bash
python --version
```
Should be Python 3.8 or higher

### Step 2: Verify PyInstaller
```bash
pyinstaller --version
```
Should show version 5.x or higher

### Step 3: Run Build
```bash
python build.py
```

### Step 4: Check Build Output
```bash
dir dist/BunnyNode/
```
Should show:
- `BunnyNode.exe`
- `_internal/` folder
- `editor/` folder with resources

### Step 5: Test Executable
```bash
dist/BunnyNode/BunnyNode.exe
```

Verify:
- [ ] Application window opens
- [ ] No error dialogs
- [ ] UI is responsive
- [ ] Can create new diagram
- [ ] Can save/load diagrams
- [ ] Can export as PNG

## Runtime Verification

When executable runs:

### ✅ Data Directory Structure
```
%USERPROFILE%/.bunnynode/
├── saves/
├── exports/
├── recent_files.json
└── your_settings.json
```

All directories should be created automatically.

### ✅ Functionality
- [ ] New diagrams can be created
- [ ] Diagrams save to `%USERPROFILE%/.bunnynode/saves/`
- [ ] Diagrams load from saves folder
- [ ] PNG exports save to `%USERPROFILE%/.bunnynode/exports/`
- [ ] Recent files list updates
- [ ] Settings are preserved

## Post-Build Steps

### ✅ Create Desktop Shortcut (Optional)
1. Right-click `dist/BunnyNode/BunnyNode.exe`
2. Select "Send to" → "Desktop (create shortcut)"
3. Rename shortcut to "BunnyNode"

### ✅ Prepare for Distribution
1. Create a ZIP file: `BunnyNode-v1.0.zip`
2. Include: `dist/BunnyNode/` folder
3. Add: README with system requirements
4. Add: Simple installation instructions

### ✅ System Requirements (for distribution)
- Windows 7 or later (64-bit recommended)
- 200MB disk space
- 256MB RAM minimum
- Python NOT required

## Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| "pyinstaller not found" | `pip install pyinstaller` |
| Build fails | `python build.py` (cleans and rebuilds) |
| Icons missing | Verify `editor/resources/` exists |
| Saves not working | Check `%USERPROFILE%/.bunnynode/` exists |
| Recent files error | Normal on first run, file will be created |
| Slow startup | Normal for PyInstaller (2-3 seconds) |

## Version Information

After successful build, document:

- **Build Date**: _____________
- **Python Version**: _____________
- **PyInstaller Version**: _____________
- **PyQt6 Version**: _____________
- **Executable Location**: dist/BunnyNode/BunnyNode.exe
- **Total Build Size**: _____________

## Success Criteria

✅ Build is complete when:
1. `python build.py` completes without errors
2. `dist/BunnyNode/BunnyNode.exe` exists
3. Executable runs and opens the application
4. Can create, save, load, and export diagrams
5. Data is stored in `%USERPROFILE%/.bunnynode/`
6. No error messages appear during use

## Next Steps After Build

1. **Test thoroughly** on different machines if possible
2. **Create backup** of successful build
3. **Document** any issues or modifications
4. **Distribute** the `dist/BunnyNode/` folder
5. **Gather feedback** from users
6. **Update** application as needed

## Support Resources

- `PYINSTALLER_BUILD.md` - Full build guide
- `PYINSTALLER_PREPARATION.md` - Detailed setup info
- `PYINSTALLER_COMPLETE.md` - Complete documentation
- `build.py` - Contains helpful comments

## Notes

- Keep `dist/` folder intact for distribution
- Don't modify files inside `_internal/` folder
- To rebuild, delete `build/` and `dist/` folders first (or use `python build.py`)
- For updates, rebuild and replace the entire `dist/BunnyNode/` folder

---

**Last Updated**: When all files were modified for PyInstaller support
**Status**: Ready for build
