"""
Template system for saving and loading preset configurations.
"""

import json
import os
from typing import Dict, Any, List, Optional


class TemplateManager:
    """Manages video generation templates."""
    
    BUILTIN_TEMPLATES = {
        'minimal': {
            'name': 'Minimal',
            'description': 'Clean and simple visualization',
            'settings': {
                'visualizer_style': 'bars',
                'color_gradient': 'monochrome',
                'monochrome_color': [255, 255, 255],
                'background_type': 'solid_color',
                'background_color': [0, 0, 0],
                'background_blur': 0,
                'background_bw': False,
                'vignette_intensity': 0,
                'strobe_enabled': False,
                'beat_sync_enabled': False,
                'visualizer_enabled': True
            }
        },
        'club': {
            'name': 'Club',
            'description': 'High-energy club style with beat sync',
            'settings': {
                'visualizer_style': 'circle',
                'color_gradient': 'pitch_rainbow',
                'background_type': 'solid_color',
                'background_color': [10, 10, 30],
                'background_blur': 0,
                'vignette_intensity': 50,
                'beat_sync_enabled': True,
                'beat_effect_type': 'flash',
                'beat_flash_color': [255, 255, 255],
                'visualizer_enabled': True
            }
        },
        'retro': {
            'name': 'Retro',
            'description': 'Nostalgic 80s style',
            'settings': {
                'visualizer_style': 'bars',
                'color_gradient': 'custom',
                'custom_color_start': [255, 0, 255],
                'custom_color_end': [0, 255, 255],
                'background_type': 'solid_color',
                'background_color': [20, 0, 40],
                'background_blur': 0,
                'vignette_intensity': 30,
                'beat_sync_enabled': True,
                'beat_effect_type': 'pulse',
                'visualizer_enabled': True
            }
        },
        'modern': {
            'name': 'Modern',
            'description': 'Contemporary clean design',
            'settings': {
                'visualizer_style': 'filled_waveform',
                'color_gradient': 'energy-based',
                'background_type': 'solid_color',
                'background_color': [15, 15, 15],
                'background_blur': 0,
                'vignette_intensity': 20,
                'beat_sync_enabled': True,
                'beat_effect_type': 'zoom',
                'visualizer_enabled': True
            }
        },
        'particle_burst': {
            'name': 'Particle Burst',
            'description': 'Dynamic particle effects',
            'settings': {
                'visualizer_style': 'particle',
                'color_gradient': 'pitch_rainbow',
                'background_type': 'solid_color',
                'background_color': [0, 0, 0],
                'background_blur': 0,
                'vignette_intensity': 0,
                'beat_sync_enabled': False,
                'visualizer_enabled': True
            }
        },
        'youtube_standard': {
            'name': 'YouTube Standard',
            'description': 'Optimized for YouTube (16:9, 1080p)',
            'settings': {
                'video_width': 1920,
                'video_height': 1080,
                'frame_rate': 30,
                'visualizer_style': 'bars',
                'color_gradient': 'frequency-based',
                'quality_preset': 'balanced',
                'encoding_preset': 'medium',
                'visualizer_enabled': True
            }
        },
        'instagram_story': {
            'name': 'Instagram Story',
            'description': 'Optimized for Instagram Stories (9:16, 1080x1920)',
            'settings': {
                'video_width': 1080,
                'video_height': 1920,
                'frame_rate': 30,
                'visualizer_style': 'circle',
                'color_gradient': 'pitch_rainbow',
                'quality_preset': 'balanced',
                'visualizer_enabled': True
            }
        },
        'tiktok': {
            'name': 'TikTok',
            'description': 'Optimized for TikTok (9:16, 1080x1920)',
            'settings': {
                'video_width': 1080,
                'video_height': 1920,
                'frame_rate': 30,
                'visualizer_style': 'filled_waveform',
                'color_gradient': 'energy-based',
                'beat_sync_enabled': True,
                'beat_effect_type': 'pulse',
                'quality_preset': 'balanced',
                'visualizer_enabled': True
            }
        }
    }
    
    def __init__(self, templates_dir: str = 'templates'):
        """
        Initialize template manager.
        
        Args:
            templates_dir: Directory to store user templates
        """
        self.templates_dir = templates_dir
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """Ensure templates directory exists."""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def get_builtin_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all built-in templates."""
        return self.BUILTIN_TEMPLATES.copy()
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template dictionary or None if not found
        """
        # Check built-in templates
        if template_id in self.BUILTIN_TEMPLATES:
            return self.BUILTIN_TEMPLATES[template_id].copy()
        
        # Check user templates
        template_path = os.path.join(self.templates_dir, f'{template_id}.json')
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading template {template_id}: {e}")
        
        return None
    
    def save_template(self, template_id: str, name: str, description: str, 
                     settings: Dict[str, Any]) -> bool:
        """
        Save a user template.
        
        Args:
            template_id: Unique template identifier
            name: Template name
            description: Template description
            settings: Settings dictionary
            
        Returns:
            True if successful, False otherwise
        """
        template = {
            'name': name,
            'description': description,
            'settings': settings
        }
        
        template_path = os.path.join(self.templates_dir, f'{template_id}.json')
        
        try:
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a user template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            True if successful, False otherwise
        """
        # Don't allow deleting built-in templates
        if template_id in self.BUILTIN_TEMPLATES:
            return False
        
        template_path = os.path.join(self.templates_dir, f'{template_id}.json')
        
        try:
            if os.path.exists(template_path):
                os.remove(template_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting template: {e}")
            return False
    
    def list_user_templates(self) -> List[Dict[str, Any]]:
        """
        List all user templates.
        
        Returns:
            List of template dictionaries with id, name, and description
        """
        templates = []
        
        if not os.path.exists(self.templates_dir):
            return templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_id = filename[:-5]  # Remove .json extension
                template = self.get_template(template_id)
                if template:
                    templates.append({
                        'id': template_id,
                        'name': template.get('name', template_id),
                        'description': template.get('description', '')
                    })
        
        return templates
    
    def list_all_templates(self) -> List[Dict[str, Any]]:
        """
        List all templates (built-in and user).
        
        Returns:
            List of template dictionaries with id, name, description, and type
        """
        templates = []
        
        # Add built-in templates
        for template_id, template in self.BUILTIN_TEMPLATES.items():
            templates.append({
                'id': template_id,
                'name': template['name'],
                'description': template['description'],
                'type': 'builtin'
            })
        
        # Add user templates
        for template in self.list_user_templates():
            template['type'] = 'user'
            templates.append(template)
        
        return templates
    
    def apply_template(self, template_id: str, current_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a template to current settings.
        
        Args:
            template_id: Template identifier
            current_settings: Current settings dictionary
            
        Returns:
            Updated settings dictionary
        """
        template = self.get_template(template_id)
        if not template:
            return current_settings
        
        template_settings = template.get('settings', {})
        
        # Merge template settings with current settings
        updated_settings = current_settings.copy()
        updated_settings.update(template_settings)
        
        return updated_settings
