"""
Settings management module for MP3 Spectrum Visualizer.
Handles saving and loading user settings.
"""

import json
import os
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages application settings save/load functionality."""
    
    DEFAULT_SETTINGS = {
        'mp3_path': '',
        'background_path': '',
        'background_fit': 'stretch',
        'background_blur': 0,
        'background_bw': False,
        'vignette_intensity': 0,
        'strobe_enabled': False,
        'strobe_color': [255, 255, 255],  # RGB
        'background_animation': 'none',
        'output_path': '',
        'auto_lyrics': False,
        'lyrics_text': '',
        'logo_path': '',
        'logo_text': '',
        'logo_position': 'top-right',
        'logo_scale': 10,
        'text_overlay': '',
        'text_position': 'center',
        'text_color': [255, 255, 255],
        'video_width': 1920,
        'video_height': 1080,
        'frame_rate': 30,
        'visualizer_enabled': True,
        'visualizer_style': 'filled_waveform',
        'color_gradient': 'pitch_rainbow',
        'orientation': 'landscape_16_9',
        'resolution': '1080p',
        # Performance settings
        'quality_preset': 'fast',  # fast, balanced, high
        'use_hardware_acceleration': True,
        'encoding_preset': 'ultrafast',  # ultrafast, fast, medium, slow
        'use_multiprocessing': True,
        'beat_sync_enabled': False,
        'video_background_path': '',
        'background_type': 'solid_color',
        'background_color': [0, 0, 0],
        # Opacity settings
        'visualizer_opacity': 100,
        'background_opacity': 100,
        'overlay_opacity': 100,
        'logo_opacity': 100,
        'text_opacity': 100,
        # Multiple backgrounds
        'background_paths': [],
        'video_background_paths': [],
        'slideshow_enabled': False,
        'slideshow_interval': 10,
        'slideshow_transition': 'fade',
        'transition_duration': 1.0,
        'auto_adjust_slideshow': False,
        # Beat shake
        'background_beat_shake_enabled': False,
        'background_beat_shake_intensity': 50,
        # Overlay effects
        'overlay_effect_type': 'none',  # none, rain, snow, sparkles, bubbles
        'overlay_video_path': '',
        # Preview settings
        'preview_duration': 10,  # seconds
        'fast_preview': True  # Enable fast preview mode by default
    }
    
    def __init__(self, settings_file: str = 'settings.json'):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings JSON file
        """
        self.settings_file = settings_file
        self.settings = self.DEFAULT_SETTINGS.copy()
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file.
        
        Returns:
            Dictionary of settings
        """
        if not os.path.exists(self.settings_file):
            return self.DEFAULT_SETTINGS.copy()
        
        try:
            with open(self.settings_file, 'r') as f:
                loaded = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            settings = self.DEFAULT_SETTINGS.copy()
            settings.update(loaded)
            self.settings = settings
            return settings
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save settings to file.
        
        Args:
            settings: Settings dictionary to save (uses self.settings if None)
            
        Returns:
            True if successful, False otherwise
        """
        if settings is not None:
            self.settings = settings
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a specific setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a specific setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
    
    def validate_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate settings dictionary.
        
        Args:
            settings: Settings to validate (uses self.settings if None)
            
        Returns:
            True if valid, False otherwise
        """
        if settings is None:
            settings = self.settings
        
        # Check that all required keys exist
        for key in self.DEFAULT_SETTINGS.keys():
            if key not in settings:
                return False
        
        # Validate specific settings
        if settings['background_fit'] not in ['stretch', 'tile', 'center']:
            return False
        
        if settings['background_animation'] not in ['none', 'fade_in']:
            return False
        
        if not (0 <= settings['background_blur'] <= 100):
            return False
        
        if not (0 <= settings['vignette_intensity'] <= 100):
            return False
        
        return True

