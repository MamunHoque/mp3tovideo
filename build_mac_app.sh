#!/bin/bash
# Build script for macOS .app bundle

echo "Building MP3 Spectrum Visualizer.app for macOS..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found."
    exit 1
fi

# Install PyInstaller if not already installed
pip install pyinstaller > /dev/null 2>&1

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "MP3 Spectrum Visualizer.app"

# Build using spec file
echo "Building application bundle..."
pyinstaller "MP3 Spectrum Visualizer.spec" --clean --noconfirm

# Check if build was successful
if [ -d "dist/MP3 Spectrum Visualizer.app" ]; then
    echo ""
    echo "✓ Build successful!"
    echo "Application bundle is located at: dist/MP3 Spectrum Visualizer.app"
    echo ""
    echo "You can now:"
    echo "  1. Test the app: open 'dist/MP3 Spectrum Visualizer.app'"
    echo "  2. Create a DMG: Use 'create_dmg.sh' script"
    echo ""
    echo "Note: ffmpeg must be installed on the target system."
    echo "Users can install it with: brew install ffmpeg"
else
    echo ""
    echo "✗ Build failed. Check the output above for errors."
    exit 1
fi



