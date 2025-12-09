#!/bin/bash
# Create a DMG file for distribution

APP_NAME="MP3 Spectrum Visualizer"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}"
DMG_PATH="dist/${DMG_NAME}.dmg"

if [ ! -d "$APP_PATH" ]; then
    echo "Error: Application bundle not found at $APP_PATH"
    echo "Please run build_mac_app.sh first"
    exit 1
fi

echo "Creating DMG file..."

# Create a temporary directory for DMG contents
TEMP_DMG_DIR="dist/dmg_temp"
rm -rf "$TEMP_DMG_DIR"
mkdir -p "$TEMP_DMG_DIR"

# Copy app to temp directory
cp -R "$APP_PATH" "$TEMP_DMG_DIR/"

# Create Applications symlink
ln -s /Applications "$TEMP_DMG_DIR/Applications"

# Create README
cat > "$TEMP_DMG_DIR/README.txt" << EOF
MP3 Spectrum Visualizer

Installation:
1. Drag "MP3 Spectrum Visualizer.app" to the Applications folder
2. Open the app from Applications

Requirements:
- macOS 10.13 or later
- ffmpeg (install with: brew install ffmpeg)

For more information, visit the project repository.
EOF

# Remove existing DMG if it exists
rm -f "$DMG_PATH"

# Create DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$TEMP_DMG_DIR" -ov -format UDZO "$DMG_PATH"

# Clean up
rm -rf "$TEMP_DMG_DIR"

if [ -f "$DMG_PATH" ]; then
    echo ""
    echo "✓ DMG created successfully!"
    echo "DMG file: $DMG_PATH"
    echo ""
    echo "You can now distribute this DMG file."
else
    echo ""
    echo "✗ DMG creation failed."
    exit 1
fi








