# MP3 Spectrum Visualizer

A Python application for creating video visualizations from MP3 audio files with customizable backgrounds, visual effects, and spectrum analysis.

## Features

- **Audio Processing**: Load and analyze MP3 files using librosa
- **Background Customization**:
  - Choose background images
  - Adjust background fit (Stretch, Tile, Center)
  - Apply blur effects
  - Convert to black & white
  - Add vignette effects
- **Visual Effects**:
  - Club strobe effect with customizable colors
  - Background animations (Fade In, etc.)
- **Spectrum Visualization**: Real-time frequency spectrum bars with color gradients
- **Additional Features**:
  - Text overlay
  - Logo overlay
  - Manual lyrics input
  - Save/Load settings
- **Preview**: Generate 5-second preview before full video generation
- **Video Generation**: Export high-quality MP4 videos with audio

## Requirements

- Python 3.8 or higher
- ffmpeg (must be installed separately and available in PATH)

## Installation

1. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install ffmpeg:
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg` (Ubuntu/Debian) or use your distribution's package manager
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Usage

1. Activate the virtual environment (if you created one):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
# Option 1: Use the run script
./run.sh

# Option 2: Run directly
python3 main.py
```

2. **Select Files**:
   - Click "Browse MP3..." to select your audio file
   - Click "Browse Background..." to select a background image (optional)

3. **Customize Settings**:
   - Adjust background fit, blur, and vignette using the controls
   - Enable/configure visual effects
   - Add text overlay or logo if desired

4. **Preview** (optional):
   - Click "Preview" to generate a 5-second preview video
   - Review the output before generating the full video

5. **Generate Video**:
   - Select an output path using "Browse..." in Output Settings
   - Click "Generate Video" to create the full video
   - Wait for the generation process to complete

6. **Save/Load Settings**:
   - Click "Save Settings" to save your current configuration
   - Click "Load Settings" to restore previously saved settings

## Project Structure

```
music/
├── main.py                 # Application entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main GUI window
│   └── preview_widget.py   # Preview display widget
├── core/
│   ├── __init__.py
│   ├── audio_processor.py  # Audio analysis and spectrum computation
│   ├── video_generator.py  # Video frame generation and assembly
│   ├── effects.py          # Visual effects implementation
│   └── settings.py         # Settings management
└── requirements.txt        # Python dependencies
```

## Technical Details

- **GUI Framework**: PyQt5
- **Audio Processing**: librosa for spectrum analysis
- **Video Processing**: ffmpeg-python for video assembly
- **Image Processing**: PIL/Pillow for image manipulation
- **Video Output**: MP4 format (H.264 video, AAC audio)
- **Default Resolution**: 1920x1080 at 30fps

## Notes

- Video generation can take time depending on audio length and system performance
- The application uses threading to prevent GUI freezing during video generation
- Temporary frame files are created during generation and automatically cleaned up
- Settings are saved to `settings.json` in the application directory

## Building for macOS Distribution

To compile the application into a standalone macOS app:

### Quick Build

```bash
# Build as .app bundle
./build_mac_app.sh

# Create DMG for distribution
./create_dmg.sh
```

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build instructions.

## Troubleshooting

- **ffmpeg not found**: Ensure ffmpeg is installed and available in your system PATH
- **Audio loading errors**: Verify the MP3 file is not corrupted and is a valid audio file
- **Video generation fails**: Check that you have write permissions for the output directory
- **Preview not showing**: Ensure an MP3 file is loaded and output path is selected
- **App won't open after build**: Right-click the app and select "Open" the first time, or run: `xattr -cr "MP3 Spectrum Visualizer.app"`

