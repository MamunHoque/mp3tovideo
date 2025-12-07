"""
Overlay effects module for MP3 Spectrum Visualizer.
Implements particle systems and video overlays (rain, snow, sparkles, bubbles).
"""

import numpy as np
from PIL import Image, ImageDraw
from typing import List, Dict, Any, Optional, Tuple
import random


class BaseOverlay:
    """Base class for overlay effects."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """
        Initialize overlay effect.
        
        Args:
            width: Image width
            height: Image height
            settings: Settings dictionary
        """
        self.width = width
        self.height = height
        self.settings = settings
        self.particles: List[Dict[str, Any]] = []
    
    def update(self, frame_number: int) -> None:
        """
        Update overlay state.
        
        Args:
            frame_number: Current frame number
        """
        raise NotImplementedError("Subclasses must implement update()")
    
    def render(self) -> Image.Image:
        """
        Render overlay effect.
        
        Returns:
            PIL Image with overlay effect
        """
        raise NotImplementedError("Subclasses must implement render()")


class RainOverlay(BaseOverlay):
    """Animated rain particles overlay."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize rain overlay."""
        super().__init__(width, height, settings)
        self.max_particles = 200
        self.spawn_rate = 5  # particles per frame
    
    def update(self, frame_number: int) -> None:
        """Update rain particles."""
        # Spawn new raindrops
        for _ in range(self.spawn_rate):
            if len(self.particles) < self.max_particles:
                self.particles.append({
                    'x': random.uniform(0, self.width),
                    'y': -10,
                    'speed': random.uniform(15, 25),
                    'length': random.uniform(10, 20),
                    'thickness': random.randint(1, 2),
                    'opacity': random.uniform(0.3, 0.8)
                })
        
        # Update existing particles
        new_particles = []
        for particle in self.particles:
            particle['y'] += particle['speed']
            
            # Keep particle if still in view
            if particle['y'] < self.height + 10:
                new_particles.append(particle)
        
        self.particles = new_particles
    
    def render(self) -> Image.Image:
        """Render rain effect."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for particle in self.particles:
            x = particle['x']
            y = particle['y']
            length = particle['length']
            
            # Draw raindrop as a line
            alpha = int(255 * particle['opacity'])
            color = (200, 200, 255, alpha)
            
            draw.line([(x, y), (x, y + length)], fill=color, width=particle['thickness'])
        
        return img


class SnowOverlay(BaseOverlay):
    """Animated snowflakes overlay."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize snow overlay."""
        super().__init__(width, height, settings)
        self.max_particles = 150
        self.spawn_rate = 3
    
    def update(self, frame_number: int) -> None:
        """Update snowflakes."""
        # Spawn new snowflakes
        for _ in range(self.spawn_rate):
            if len(self.particles) < self.max_particles:
                self.particles.append({
                    'x': random.uniform(0, self.width),
                    'y': -10,
                    'speed': random.uniform(2, 5),
                    'drift': random.uniform(-1, 1),
                    'size': random.uniform(2, 6),
                    'opacity': random.uniform(0.4, 0.9),
                    'swing': random.uniform(0, 6.28),  # Random phase for swing
                    'swing_speed': random.uniform(0.05, 0.15)
                })
        
        # Update existing particles
        new_particles = []
        for particle in self.particles:
            particle['y'] += particle['speed']
            particle['swing'] += particle['swing_speed']
            particle['x'] += np.sin(particle['swing']) * 2 + particle['drift']
            
            # Keep particle if still in view
            if particle['y'] < self.height + 10 and 0 <= particle['x'] <= self.width:
                new_particles.append(particle)
        
        self.particles = new_particles
    
    def render(self) -> Image.Image:
        """Render snow effect."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for particle in self.particles:
            x = int(particle['x'])
            y = int(particle['y'])
            size = int(particle['size'])
            
            alpha = int(255 * particle['opacity'])
            color = (255, 255, 255, alpha)
            
            # Draw snowflake as a circle
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
        
        return img


class SparklesOverlay(BaseOverlay):
    """Twinkling sparkle particles overlay."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize sparkles overlay."""
        super().__init__(width, height, settings)
        self.max_particles = 100
        self.spawn_rate = 2
    
    def update(self, frame_number: int) -> None:
        """Update sparkles."""
        # Spawn new sparkles
        for _ in range(self.spawn_rate):
            if len(self.particles) < self.max_particles:
                self.particles.append({
                    'x': random.uniform(0, self.width),
                    'y': random.uniform(0, self.height),
                    'life': 1.0,
                    'decay': random.uniform(0.02, 0.05),
                    'size': random.uniform(2, 5),
                    'color': (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(150, 255)
                    ),
                    'twinkle_phase': random.uniform(0, 6.28),
                    'twinkle_speed': random.uniform(0.1, 0.3)
                })
        
        # Update existing particles
        new_particles = []
        for particle in self.particles:
            particle['life'] -= particle['decay']
            particle['twinkle_phase'] += particle['twinkle_speed']
            
            if particle['life'] > 0:
                new_particles.append(particle)
        
        self.particles = new_particles
    
    def render(self) -> Image.Image:
        """Render sparkles effect."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for particle in self.particles:
            x = int(particle['x'])
            y = int(particle['y'])
            
            # Twinkling effect
            twinkle = (np.sin(particle['twinkle_phase']) + 1) / 2
            size = int(particle['size'] * twinkle)
            
            alpha = int(255 * particle['life'] * twinkle)
            color = (*particle['color'], alpha)
            
            # Draw sparkle with a cross pattern
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
            
            # Add cross lines for sparkle effect
            if size > 2:
                line_color = (*particle['color'], alpha // 2)
                draw.line([(x - size * 2, y), (x + size * 2, y)], fill=line_color, width=1)
                draw.line([(x, y - size * 2), (x, y + size * 2)], fill=line_color, width=1)
        
        return img


class BubblesOverlay(BaseOverlay):
    """Rising bubbles effect overlay."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize bubbles overlay."""
        super().__init__(width, height, settings)
        self.max_particles = 80
        self.spawn_rate = 2
    
    def update(self, frame_number: int) -> None:
        """Update bubbles."""
        # Spawn new bubbles from bottom
        for _ in range(self.spawn_rate):
            if len(self.particles) < self.max_particles:
                self.particles.append({
                    'x': random.uniform(0, self.width),
                    'y': self.height + 10,
                    'speed': random.uniform(1, 3),
                    'drift': random.uniform(-0.5, 0.5),
                    'size': random.uniform(5, 15),
                    'opacity': random.uniform(0.2, 0.5),
                    'wobble': random.uniform(0, 6.28),
                    'wobble_speed': random.uniform(0.05, 0.1)
                })
        
        # Update existing particles
        new_particles = []
        for particle in self.particles:
            particle['y'] -= particle['speed']
            particle['wobble'] += particle['wobble_speed']
            particle['x'] += np.sin(particle['wobble']) * 1 + particle['drift']
            
            # Keep particle if still in view
            if particle['y'] > -20 and 0 <= particle['x'] <= self.width:
                new_particles.append(particle)
        
        self.particles = new_particles
    
    def render(self) -> Image.Image:
        """Render bubbles effect."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for particle in self.particles:
            x = int(particle['x'])
            y = int(particle['y'])
            size = int(particle['size'])
            
            alpha = int(255 * particle['opacity'])
            
            # Draw bubble outline
            outline_color = (200, 230, 255, alpha)
            draw.ellipse([x - size, y - size, x + size, y + size], outline=outline_color, width=2)
            
            # Add highlight
            highlight_alpha = int(alpha * 0.6)
            highlight_color = (255, 255, 255, highlight_alpha)
            highlight_size = size // 3
            draw.ellipse([
                x - size // 2, y - size // 2,
                x - size // 2 + highlight_size, y - size // 2 + highlight_size
            ], fill=highlight_color)
        
        return img


class OverlayFactory:
    """Factory for creating overlay effects."""
    
    @staticmethod
    def create(overlay_type: str, width: int, height: int, settings: Dict[str, Any]) -> Optional[BaseOverlay]:
        """
        Create overlay instance.
        
        Args:
            overlay_type: Overlay type name
            width: Image width
            height: Image height
            settings: Settings dictionary
            
        Returns:
            Overlay instance or None
        """
        overlay_type = overlay_type.lower().replace(' ', '_')
        
        if overlay_type == 'rain':
            return RainOverlay(width, height, settings)
        elif overlay_type == 'snow':
            return SnowOverlay(width, height, settings)
        elif overlay_type == 'sparkles':
            return SparklesOverlay(width, height, settings)
        elif overlay_type == 'bubbles':
            return BubblesOverlay(width, height, settings)
        elif overlay_type == 'none':
            return None
        else:
            return None

