# Multiple Backgrounds Feature

## ✅ New Features Added

### 1. Multiple Image Backgrounds
**Location:** Background Tab → Background Image section

**Features:**
- **List Widget** - Shows all selected background images
- **"Add Images..." Button** - Select multiple images at once
  - Hold **Ctrl/Cmd** + Click to select multiple files
  - Hold **Shift** + Click to select a range
- **"Remove Selected" Button** - Remove selected images from list
- **"Clear All" Button** - Clear all backgrounds

### 2. Multiple Video Backgrounds
**Location:** Background Tab → Background Video section (when Video type selected)

**Features:**
- **List Widget** - Shows all selected background videos
- **"Add Videos..." Button** - Select multiple videos at once
  - Supports: MP4, MOV, AVI, MKV formats
  - Hold **Ctrl/Cmd** + Click to select multiple files
- **"Remove Selected" Button** - Remove selected videos
- **"Clear All" Button** - Clear all videos

### 3. Slideshow Controls

#### Enable Slideshow
- **Checkbox**: Enable slideshow mode to cycle through backgrounds

#### Interval (5-60 seconds)
- **Slider**: Set how long each background/video shows before transitioning

#### Transition Type
- **Fade** - Smooth fade between backgrounds
- **Crossfade** - Blend fade effect
- **Slide** - Slide from left
- **Zoom** - Zoom out effect
- **Instant** - Quick cut (no transition)

#### Duration (0.5-3.0 seconds)
- **Slider**: Control how long the transition effect lasts

### 4. 🎵 Auto-Adjust to Music Duration

**New Feature:** "Auto-adjust timing to cover music duration"

This intelligent feature automatically calculates the optimal slideshow interval to ensure your backgrounds perfectly cover your entire music duration!

**How it works:**
1. Select multiple backgrounds (images or videos)
2. Load your music file
3. Enable "Slideshow"
4. Check "Auto-adjust timing to cover music duration"
5. ✨ The app automatically calculates: `interval = (music_duration - transition_time) / number_of_backgrounds`

**Example:**
- Music: 180 seconds (3 minutes)
- Backgrounds: 5 images
- Transition duration: 1 second
- **Auto-calculated interval**: (180 - 4×1) / 5 = **35.2 seconds per image**

Result: Your 5 backgrounds will perfectly cover the entire 3-minute song! 🎉

## How to Use

### For Multiple Images:

1. **Select Background Type**: Choose "Image" from Background Type dropdown
2. **Add Images**: Click "Add Images..." button
3. **Select Multiple**: 
   - Hold **Ctrl** (Windows/Linux) or **Cmd** (Mac) and click multiple images
   - Or hold **Shift** to select a range
4. **Enable Slideshow**: Check "Enable Slideshow" checkbox
5. **Choose Transition**: Select your preferred transition effect
6. **Auto-Adjust (Optional)**: 
   - Load your music file first
   - Check "Auto-adjust timing to cover music duration"
   - Interval will be calculated automatically!

### For Multiple Videos:

1. **Select Background Type**: Choose "Video" from Background Type dropdown
2. **Add Videos**: Click "Add Videos..." button
3. **Select Multiple**: Hold **Ctrl/Cmd** and click multiple videos
4. **Enable Slideshow**: Check "Enable Slideshow" checkbox
5. **Configure**: Set interval and transition (or use auto-adjust)

## Settings Storage

All settings are automatically saved:
```python
{
    'background_paths': ['path/to/image1.jpg', 'path/to/image2.png', ...],
    'video_background_paths': ['path/to/video1.mp4', 'path/to/video2.mov', ...],
    'slideshow_enabled': True/False,
    'slideshow_interval': 10,  # seconds
    'slideshow_transition': 'fade',  # fade, crossfade, slide, zoom, instant
    'transition_duration': 1.0,  # seconds
    'auto_adjust_slideshow': True/False  # NEW!
}
```

## Technical Implementation

### Backend (`core/video_generator.py`)
- **BackgroundManager** class handles slideshow logic
- Supports both image and video paths
- Caches backgrounds for performance
- Calculates which background to show based on frame number
- Applies transitions between backgrounds

### Frontend (`gui/main_window.py`)
- QListWidget for managing multiple files
- Add/Remove/Clear buttons for easy management
- Auto-adjust calculation on audio load
- Real-time preview updates when backgrounds change

## Benefits

✅ **Creative Freedom** - Use as many backgrounds as you want
✅ **Perfect Timing** - Auto-adjust ensures backgrounds cover entire song
✅ **Smooth Transitions** - 5 transition types to choose from
✅ **Easy Management** - Simple list interface with add/remove buttons
✅ **Mixed Media** - Use images or videos, even mix them
✅ **Performance** - Intelligent caching for smooth playback
✅ **User-Friendly** - Visual list shows all selected backgrounds

## Example Use Cases

### 1. Photo Montage
- Add 20 photos from an event
- Enable auto-adjust
- Each photo gets equal time
- Perfect for tribute videos or slideshows

### 2. Dynamic Backgrounds
- Mix 5-10 different video clips
- Use fade transitions
- Creates dynamic, constantly changing background

### 3. Story Progression
- Use 3-4 themed backgrounds
- Long intervals (30-60s each)
- Instant transitions for dramatic effect

### 4. Music Video Style
- Multiple high-energy video clips
- Short intervals (5-10s)
- Zoom or slide transitions
- Perfect for energetic music

## Tips

💡 **For Best Results:**
- Use images/videos with similar aspect ratios
- Enable "Auto-adjust timing" for perfectly timed slideshows
- Use "Fade" or "Crossfade" for smooth, professional look
- Use "Instant" or "Zoom" for energetic, fast-paced content
- Test with preview before generating full video

💡 **Performance:**
- Images are cached for better performance
- Up to 10 backgrounds cached simultaneously
- Videos are streamed on-demand
- No limit on number of backgrounds!

## Keyboard Shortcuts

When list is focused:
- **Delete** - Remove selected items
- **Ctrl+A** - Select all items
- **Shift+Click** - Select range
- **Ctrl+Click** - Toggle selection

Enjoy creating dynamic, multi-background music videos! 🎬🎵



