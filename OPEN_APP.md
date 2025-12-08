# How to Open the Built Application

## Important: You Should Open the .app Bundle, Not the .pkg File

The `.pkg` file in the `build/` folder is an **intermediate PyInstaller file** - it's not meant to be opened directly.

## The Actual Application

The built application is located at:
```
dist/MP3 Spectrum Visualizer.app
```

## Opening the Application

### Method 1: Right-Click and Open (First Time)

1. Navigate to `dist/` folder
2. Find `MP3 Spectrum Visualizer.app`
3. **Right-click** on it
4. Select **"Open"** from the context menu
5. Click **"Open"** in the security dialog

This is required the first time because macOS Gatekeeper blocks unsigned apps.

### Method 2: Fix Permissions First

Run the fix permissions script:

```bash
./fix_permissions.sh
```

Then double-click the app normally.

### Method 3: Command Line

```bash
open "dist/MP3 Spectrum Visualizer.app"
```

### Method 4: Remove Quarantine Manually

If you still have issues:

```bash
xattr -cr "dist/MP3 Spectrum Visualizer.app"
chmod +x "dist/MP3 Spectrum Visualizer.app/Contents/MacOS/MP3 Spectrum Visualizer"
```

Then try opening it again.

## If the App Still Won't Open

1. **Check Console for errors:**
   ```bash
   open Console.app
   ```
   Look for error messages related to the app.

2. **Try running from terminal:**
   ```bash
   "dist/MP3 Spectrum Visualizer.app/Contents/MacOS/MP3 Spectrum Visualizer"
   ```
   This will show any error messages.

3. **Check System Preferences:**
   - Go to System Preferences → Security & Privacy
   - Check if the app is blocked there
   - Click "Open Anyway" if it appears

## Using the DMG File

If you created a DMG file (`dist/MP3 Spectrum Visualizer.dmg`):

1. Double-click the DMG file to mount it
2. Drag `MP3 Spectrum Visualizer.app` to the Applications folder
3. Open it from Applications (right-click → Open the first time)







