#!/bin/bash
# Clean rebuild script for macOS app

echo "Cleaning previous build..."
rm -rf build dist "MP3 Spectrum Visualizer.app"

echo ""
echo "Rebuilding application..."
./build_mac_app.sh

echo ""
echo "Fixing permissions..."
./fix_permissions.sh

echo ""
echo "Build complete! Try opening:"
echo "  open 'dist/MP3 Spectrum Visualizer.app'"
echo ""
echo "Or right-click the app and select 'Open' (first time only)"





