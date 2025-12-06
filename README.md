# MP3 to Video Generator

A professional Python application for creating stunning video visualizations from MP3 audio files with advanced features including video backgrounds, beat detection, multiple visualizer styles, and platform-specific export presets.

## Features

### Audio Analysis
- **Beat Detection**: Automatic tempo and beat detection using librosa
- **Spectrum Analysis**: Real-time frequency analysis with 64 frequency bands
- **Audio Intensity Tracking**: Dynamic effects based on audio energy

### Background Options
- **Video Backgrounds**: Use MP4 videos as animated backgrounds with looping support
- **Image Backgrounds**: Static images with fit modes (Stretch, Tile, Center)
- **Solid Colors**: Simple solid color backgrounds
- **Effects**: Blur, vignette, black & white conversion

### Visualizer Styles
- **Bars**: Classic spectrum bars with color gradients
- **Filled Waveform**: Smooth audio waveform visualization
- **Circle**: Circular spectrum analyzer radiating from center
- **Line Waveform**: Traditional oscilloscope-style waveform
- **Particle System**: Dynamic audio-reactive particles

### Color Gradients
- **Pitch Rainbow**: Full spectrum rainbow based on frequency
- **Frequency-based**: Low=red, mid=green, high=blue
- **Energy-based**: Color intensity based on amplitude
- **Custom**: User-defined gradient colors
- **Monochrome**: Single color with varying intensity

### Beat-Synchronized Effects
- **Pulse**: Scale effect on beats
- **Flash**: White flash on beats
- **Strobe**: Beat-synced strobe lighting
- **Zoom**: Zoom in/out on beats

### Templates & Presets
- **Built-in Templates**: Minimal, Club, Retro, Modern, Particle Burst
- **Platform Presets**: YouTube, Instagram Story, TikTok optimized settings
- **Custom Templates**: Save and load your own configurations

### Performance Optimization
- **Quality Presets**: Fast, Balanced, High quality modes
- **Hardware Acceleration**: VideoToolbox (macOS) support
- **Multiprocessing**: Parallel frame generation for faster rendering
- **Progress Tracking**: Real-time FPS counter and ETA

### Additional Features
- **Text Overlay**: Add custom text with positioning
- **Logo Overlay**: Brand your videos
- **Real-time Preview**: Preview with playback before generating
- **Multiple Resolutions**: 480p to 4K support
- **Multiple Orientations**: Landscape, Portrait, Square, Ultrawide

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

