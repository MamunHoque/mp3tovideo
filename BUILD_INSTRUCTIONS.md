# Building MP3 Spectrum Visualizer for macOS

This guide explains how to compile and package the MP3 Spectrum Visualizer application for macOS distribution.

## Prerequisites

1. **macOS Development Environment**
   - macOS 10.13 or later
   - Xcode Command Line Tools (install with: `xcode-select --install`)

2. **Python Environment**
   - Python 3.8 or later
   - Virtual environment with all dependencies installed

3. **Required System Tools**
   - ffmpeg (for video processing)
   - PyInstaller (will be installed automatically)

## Quick Build

### Option 1: Single Executable File

```bash
./build_mac.sh
```

This creates a single executable file at `dist/MP3 Spectrum Visualizer`.

### Option 2: macOS Application Bundle (.app)

```bash
./build_mac_app.sh
```

This creates a proper macOS application bundle at `dist/MP3 Spectrum Visualizer.app`.

### Option 3: Create DMG for Distribution

After building the .app bundle:

```bash
./create_dmg.sh
```

This creates a DMG file at `dist/MP3 Spectrum Visualizer.dmg` that users can mount and drag the app to Applications.

## Manual Build Steps

If you prefer to build manually:

### 1. Install PyInstaller

```bash
source venv/bin/activate
pip install pyinstaller
```

### 2. Build Application Bundle

```bash
pyinstaller "MP3 Spectrum Visualizer.spec" --clean --noconfirm
```

### 3. Test the Application

```bash
open "dist/MP3 Spectrum Visualizer.app"
```

## Customizing the Build

### Modify the Spec File

Edit `MP3 Spectrum Visualizer.spec` to customize:
- Application name
- Bundle identifier
- Version information
- Icon file (add an `.icns` file and reference it)
- Additional data files

### Adding an Icon

1. Create or obtain an `.icns` file
2. Place it in the project root
3. Update the spec file:
   ```python
   icon='icon.icns',
   ```

### Code Signing (Optional)

For distribution outside the App Store, you may want to code sign:

```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "dist/MP3 Spectrum Visualizer.app"
```

### Notarization (Optional)

For Gatekeeper compatibility:

```bash
xcrun notarytool submit "dist/MP3 Spectrum Visualizer.dmg" --keychain-profile "notarytool-profile" --wait
```

## Distribution Notes

### User Requirements

Users need to have:
- macOS 10.13 or later
- ffmpeg installed (they can install with: `brew install ffmpeg`)

### Including ffmpeg

If you want to bundle ffmpeg with the app:

1. Copy ffmpeg binary to a `bin` directory in your project
2. Update the spec file to include it:
   ```python
   binaries=[('bin/ffmpeg', 'bin')],
   ```
3. Update your code to use the bundled ffmpeg path

### File Size

The built application will be large (100-200MB) due to:
- Python runtime
- PyQt5 libraries
- NumPy, SciPy, scikit-learn
- Librosa and audio processing libraries

This is normal for Python applications packaged with PyInstaller.

## Troubleshooting

### "App is damaged" Error

If users see "App is damaged" when opening:
1. They need to right-click and select "Open" the first time
2. Or remove the quarantine attribute: `xattr -cr "MP3 Spectrum Visualizer.app"`

### Missing Dependencies

If the app crashes with import errors:
1. Check the PyInstaller output for missing modules
2. Add them to `hiddenimports` in the spec file
3. Rebuild

### ffmpeg Not Found

The app requires ffmpeg to be installed separately. Users can:
- Install via Homebrew: `brew install ffmpeg`
- Or download from https://ffmpeg.org/download.html

## Advanced: Creating a Standalone Distribution

To create a completely standalone app that doesn't require Python:

1. Use PyInstaller with `--onefile` (already in spec)
2. Bundle all dependencies
3. Include ffmpeg binary
4. Test on a clean macOS system

## Build Output

After building, you'll find:
- `dist/MP3 Spectrum Visualizer.app` - The application bundle
- `build/` - Temporary build files (can be deleted)
- `MP3 Spectrum Visualizer.spec` - PyInstaller spec file (keep this)

## Distribution Checklist

- [ ] Build the application bundle
- [ ] Test on a clean macOS system
- [ ] Verify ffmpeg requirement is documented
- [ ] Create DMG file for distribution
- [ ] (Optional) Code sign the application
- [ ] (Optional) Notarize the DMG
- [ ] Test installation from DMG
- [ ] Create release notes



