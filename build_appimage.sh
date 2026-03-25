#!/bin/bash
# Local script to build an AppImage using python-appimage

echo "Building AppImage..."

# We need a build directory structure
mkdir -p build_dir
cp main.py build_dir/
cp sta-tool.desktop build_dir/
cp requirements.txt build_dir/
cp -r core build_dir/
cp -r ui build_dir/
cp -r plugins build_dir/
cp -r assets build_dir/ 

# Try to use python-appimage to bundle it
./venv/bin/python -m python_appimage build app build_dir

echo "AppImage built successfully!"
