#!/usr/bin/env python
"""
Build script for BunnyNode Diagram Editor
Compiles the application using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("✗ PyInstaller not installed")
        print("Install it with: pip install pyinstaller")
        return False


def clean_build():
    """Clean previous build artifacts"""
    print("\n📦 Cleaning previous builds...")
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}")
    
    if os.path.exists('BunnyNode.spec'):
        os.remove('BunnyNode.spec')
        print("  Removed BunnyNode.spec")


def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building executable...")
    
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--onedir',  # Create a directory with all dependencies
        '--windowed',  # No console window
        '--name',
        'BunnyNode',
        '--icon=editor/resources/icons/window.png',
        '--add-data=editor/resources:editor/resources',
        '--add-data=editor/recent_files.json:editor',
        '--add-data=editor/default_settings.json:editor',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        'main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed with error code {e.returncode}")
        return False


def verify_build():
    """Verify that the build was successful"""
    print("\n✓ Verifying build...")
    
    expected_dir = Path('dist') / 'BunnyNode'
    expected_exe = expected_dir / 'BunnyNode.exe'
    
    if expected_dir.exists():
        print(f"✓ Build directory found: {expected_dir}")
    else:
        print(f"✗ Build directory not found: {expected_dir}")
        return False
    
    if expected_exe.exists():
        print(f"✓ Executable found: {expected_exe}")
    else:
        print(f"✗ Executable not found: {expected_exe}")
        return False
    
    return True


def print_info():
    """Print build information"""
    print("\n" + "="*60)
    print("BunnyNode - Diagram Editor Build Script")
    print("="*60)
    print("\nBuild Information:")
    print("  - Target: Windows executable")
    print("  - Output: dist/BunnyNode/")
    print("  - Console: None (windowed application)")
    print("\nThe executable will:")
    print("  - Store saves in: %USERPROFILE%/.bunnynode/saves/")
    print("  - Store exports in: %USERPROFILE%/.bunnynode/exports/")
    print("  - Store settings in: %USERPROFILE%/.bunnynode/your_settings.json")
    print("="*60 + "\n")


def main():
    """Main build function"""
    print_info()
    
    # Check dependencies
    if not check_pyinstaller():
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build the executable
    if not build_executable():
        sys.exit(1)
    
    # Verify the build
    if verify_build():
        print("\n✅ Build successful!")
        print("\nYou can now run the application from:")
        print("  dist/BunnyNode/BunnyNode.exe")
        print("\nOr create a shortcut to the executable for easier access.")
    else:
        print("\n❌ Build verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()