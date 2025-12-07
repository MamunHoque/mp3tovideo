#!/bin/bash
# Build script for macOS application

echo "Building MP3 Spectrum Visualizer for macOS..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Install PyInstaller if not already installed
pip install pyinstaller > /dev/null 2>&1

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Build the application
echo "Building application..."
pyinstaller --name="MP3 Spectrum Visualizer" \
    --windowed \
    --onefile \
    --icon=NONE \
    --add-data "core:core" \
    --add-data "gui:gui" \
    --hidden-import=PyQt5 \
    --hidden-import=librosa \
    --hidden-import=numpy \
    --hidden-import=PIL \
    --hidden-import=ffmpeg \
    --hidden-import=soundfile \
    --collect-all=librosa \
    --collect-all=numpy \
    --collect-all=scipy \
    --collect-all=sklearn \
    --noconfirm \
    main.py

# Check if build was successful
if [ -f "dist/MP3 Spectrum Visualizer" ]; then
    echo ""
    echo "✓ Build successful!"
    echo "Application is located at: dist/MP3 Spectrum Visualizer"
    echo ""
    echo "Note: ffmpeg must be installed on the target system."
    echo "Users can install it with: brew install ffmpeg"
else
    echo ""
    echo "✗ Build failed. Check the output above for errors."
    exit 1
fi





