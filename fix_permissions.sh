#!/bin/bash
# Fix permissions and remove quarantine attributes for macOS app

APP_NAME="MP3 Spectrum Visualizer"
APP_PATH="dist/${APP_NAME}.app"

if [ ! -d "$APP_PATH" ]; then
    echo "Error: Application bundle not found at $APP_PATH"
    echo "Please build the app first with: ./build_mac_app.sh"
    exit 1
fi

echo "Fixing permissions for ${APP_NAME}.app..."

# Remove quarantine attribute (allows app to open without Gatekeeper blocking)
xattr -cr "$APP_PATH"

# Make sure the executable inside has proper permissions
# Find the actual executable name (might be different)
EXECUTABLE=$(find "$APP_PATH/Contents/MacOS" -type f -perm +111 2>/dev/null | head -1)
if [ -n "$EXECUTABLE" ]; then
    chmod +x "$EXECUTABLE"
fi

# Make the app bundle readable
chmod -R u+r "$APP_PATH"

echo ""
echo "✓ Permissions fixed!"
echo ""
echo "You can now open the app by:"
echo "  1. Right-click and select 'Open' (first time only)"
echo "  2. Or run: open '$APP_PATH'"
echo ""

