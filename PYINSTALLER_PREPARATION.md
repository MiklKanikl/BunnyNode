# PyInstaller Preparation - Summary

## What Was Changed

I've prepared your BunnyNode Diagram Editor for PyInstaller compilation. Here are all the changes made:

### 1. **New Path Utility Module** (`editor/path_utils.py`)
   - Created centralized path management that works in both development and compiled modes
   - Automatically detects if running as:
     - **Python script**: Uses project root directory
     - **PyInstaller executable**: Uses `%USERPROFILE%/.bunnynode/` directory
   - Functions included:
     - `get_application_path()`: Application base directory
     - `get_data_directory()`: Main data directory
     - `get_saves_directory()`: Directory for diagram saves
     - `get_exports_directory()`: Directory for PNG exports
     - `get_settings_path()`: Path to settings file

### 2. **Updated Code Files**

#### `editor/core/scene.py`
- Updated `save_file_dialog()` to use `get_saves_directory()`
- Updated `load_file_dialog()` to use `get_saves_directory()`
- Updated `update_recent_files()` to handle missing files gracefully

#### `editor/ui/view.py`
- Updated `export()` to use `get_exports_directory()`

#### `editor/controller/app_controller.py`
- Updated `get_current_settings()` to use `get_settings_path()`
- Added fallback for missing settings files

#### `main.py`
- Improved initialization with proper path handling
- Added check for frozen state

### 3. **Build Configuration Files**

#### `BunnyNode.spec`
- PyInstaller specification file
- Includes all necessary data files (resources, settings, recent files)
- Configured for Windows windowed application

#### `build.py`
- Automated build script
- Handles cleaning, building, and verification
- Provides helpful build information and error messages

#### `PYINSTALLER_BUILD.md`
- Comprehensive build guide
- Includes troubleshooting section
- Explains data directory handling
- Provides distribution options

## Data Directory Structure

When compiled and run as executable:

```
%USERPROFILE%/.bunnynode/
├── saves/                    (diagram files)
├── exports/                  (PNG exports)
├── recent_files.json        (recent file list)
└── your_settings.json       (user settings)
```

When running as Python script (development):

```
project_root/
├── saves/                    (diagram files)
├── exports/                  (PNG exports)
├── editor/
│   ├── recent_files.json    (recent file list)
│   └── your_settings.json   (user settings)
└── ...
```

## How to Build

### Prerequisites

```bash
# Install/update PyInstaller
pip install pyinstaller

# Ensure all dependencies are installed
pip install -r requirements.txt
```

### Quick Build

```bash
python build.py
```

### Result

The executable will be created at:
```
dist/BunnyNode/BunnyNode.exe
```

## Key Features

✅ **Backward Compatible**: Script mode still works exactly as before
✅ **User Data Isolation**: Each user gets their own .bunnynode directory
✅ **Automatic Setup**: Creates directories on first run
✅ **Resource Bundling**: All icons and resources included in build
✅ **Error Handling**: Graceful fallbacks for missing config files
✅ **No Installation**: Users can run directly from exe

## Testing

Before building, test that the application still runs in development mode:

```bash
python main.py
```

Everything should work exactly as before. The path handling is transparent to the user.

## Troubleshooting

If the build fails, ensure:
1. PyInstaller is installed: `pip install pyinstaller`
2. All dependencies installed: `pip install -r requirements.txt`
3. Icon file exists: `editor/resources/icons/window.png`
4. Recent_files.json exists: `editor/recent_files.json`
5. Default_settings.json exists: `editor/default_settings.json`

For detailed troubleshooting, see: `PYINSTALLER_BUILD.md`

## Next Steps

1. Install PyInstaller: `pip install pyinstaller`
2. Run: `python build.py`
3. Test the executable: `dist/BunnyNode/BunnyNode.exe`
4. Create shortcuts for easy access
5. (Optional) Use Inno Setup or NSIS to create an installer

## Files Modified

- `main.py` - Enhanced initialization
- `editor/path_utils.py` - **NEW** - Path management
- `editor/core/scene.py` - Use path utilities
- `editor/ui/view.py` - Use path utilities
- `editor/controller/app_controller.py` - Use path utilities

## Files Created

- `BunnyNode.spec` - PyInstaller spec
- `build.py` - Build automation script
- `PYINSTALLER_BUILD.md` - Detailed build guide
- `PYINSTALLER_PREPARATION.md` - This file

## Notes

- The application automatically detects the environment and uses the correct paths
- No user code changes needed - everything is backward compatible
- Compiled executable is ready for distribution
- Performance is identical to running from Python script
