"""
Visualizer module for different audio visualization styles.
Implements various visualizer types with customizable colors and effects.
"""

import numpy as np
from PIL import Image, ImageDraw
from typing import Tuple, Optional, Dict, Any
import math


class BaseVisualizer:
    """Base class for all visualizers."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """
        Initialize visualizer.
        
        Args:
            width: Image width
            height: Image height
            settings: Settings dictionary
        """
        self.width = width
        self.height = height
        self.settings = settings
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """
        Render visualization.
        
        Args:
            bands: Frequency band magnitudes
            spectrum_data: Full spectrum data
            frame_number: Current frame number
            
        Returns:
            PIL Image with visualization
        """
        raise NotImplementedError("Subclasses must implement render()")
    
    def get_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """
        Get color for visualization based on gradient settings.
        
        Args:
            index: Current index
            total: Total number of elements
            magnitude: Magnitude value (0.0 to 1.0)
            
        Returns:
            RGBA color tuple
        """
        gradient_type = self.settings.get('color_gradient', 'frequency-based')
        
        if gradient_type == 'pitch_rainbow':
            return self._pitch_rainbow_color(index, total, magnitude)
        elif gradient_type == 'frequency-based':
            return self._frequency_based_color(index, total, magnitude)
        elif gradient_type == 'energy-based':
            return self._energy_based_color(magnitude)
        elif gradient_type == 'custom':
            return self._custom_color(index, total, magnitude)
        elif gradient_type == 'monochrome':
            return self._monochrome_color(magnitude)
        else:
            return self._frequency_based_color(index, total, magnitude)
    
    def _pitch_rainbow_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Rainbow spectrum based on pitch/frequency."""
        # Map index to hue (0-360)
        hue = (index / total) * 360
        # Convert HSV to RGB
        h = hue / 60
        x = 1 - abs((h % 2) - 1)
        
        if h < 1:
            r, g, b = 1, x, 0
        elif h < 2:
            r, g, b = x, 1, 0
        elif h < 3:
            r, g, b = 0, 1, x
        elif h < 4:
            r, g, b = 0, x, 1
        elif h < 5:
            r, g, b = x, 0, 1
        else:
            r, g, b = 1, 0, x
        
        # Apply magnitude as brightness
        brightness = 0.5 + (magnitude * 0.5)
        r = int(r * 255 * brightness)
        g = int(g * 255 * brightness)
        b = int(b * 255 * brightness)
        
        return (r, g, b, 255)
    
    def _frequency_based_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Color based on frequency range: low=red, mid=green, high=blue."""
        if index < total / 3:
            # Low frequency - red to yellow
            r = 255
            g = int(255 * (index / (total / 3)))
            b = 0
        elif index < total * 2 / 3:
            # Mid frequency - yellow to cyan
            r = int(255 * (1 - (index - total / 3) / (total / 3)))
            g = 255
            b = int(255 * ((index - total / 3) / (total / 3)))
        else:
            # High frequency - cyan to blue
            r = 0
            g = int(255 * (1 - (index - total * 2 / 3) / (total / 3)))
            b = 255
        
        return (r, g, b, 255)
    
    def _energy_based_color(self, magnitude: float) -> Tuple[int, int, int, int]:
        """Color intensity based on energy/amplitude."""
        # Blue to red gradient based on energy
        if magnitude < 0.33:
            r = 0
            g = int(magnitude * 3 * 255)
            b = 255
        elif magnitude < 0.66:
            r = int((magnitude - 0.33) * 3 * 255)
            g = 255
            b = int((1 - (magnitude - 0.33) * 3) * 255)
        else:
            r = 255
            g = int((1 - (magnitude - 0.66) * 3) * 255)
            b = 0
        
        return (r, g, b, 255)
    
    def _custom_color(self, index: int, total: int, magnitude: float) -> Tuple[int, int, int, int]:
        """Custom gradient between two user-defined colors."""
        start_color = self.settings.get('custom_color_start', [255, 0, 255])
        end_color = self.settings.get('custom_color_end', [0, 255, 255])
        
        # Interpolate between start and end colors
        t = index / total if total > 0 else 0
        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
        
        # Apply magnitude as brightness
        brightness = 0.5 + (magnitude * 0.5)
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        
        return (r, g, b, 255)
    
    def _monochrome_color(self, magnitude: float) -> Tuple[int, int, int, int]:
        """Single color with varying intensity."""
        base_color = self.settings.get('monochrome_color', [255, 255, 255])
        
        r = int(base_color[0] * magnitude)
        g = int(base_color[1] * magnitude)
        b = int(base_color[2] * magnitude)
        
        return (r, g, b, 255)


class BarsVisualizer(BaseVisualizer):
    """Classic spectrum bars visualization."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render spectrum bars."""
        num_bands = len(bands)
        bar_width = self.width // num_bands
        bar_spacing = 2
        
        # Create transparent image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw bars
        for i, magnitude in enumerate(normalized_bands):
            bar_height = int(magnitude * self.height * 0.8)
            x = i * bar_width + bar_spacing
            
            color = self.get_color(i, num_bands, magnitude)
            
            # Draw bar from bottom
            y1 = self.height - bar_height
            y2 = self.height
            draw.rectangle([x, y1, x + bar_width - bar_spacing, y2], fill=color)
        
        return img


class FilledWaveformVisualizer(BaseVisualizer):
    """Filled waveform visualization."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render filled waveform."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_points = len(bands)
        if num_points < 2:
            return img
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Create waveform points
        points_top = []
        points_bottom = []
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            x = int((i / num_points) * self.width)
            wave_height = int(magnitude * self.height * 0.4)
            
            points_top.append((x, center_y - wave_height))
            points_bottom.append((x, center_y + wave_height))
        
        # Draw filled polygon
        all_points = points_top + points_bottom[::-1]
        
        # Get average color
        avg_magnitude = np.mean(normalized_bands)
        color = self.get_color(num_points // 2, num_points, avg_magnitude)
        
        if len(all_points) >= 3:
            draw.polygon(all_points, fill=color)
        
        return img


class CircleVisualizer(BaseVisualizer):
    """Circular spectrum analyzer."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render circular spectrum."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_bands = len(bands)
        center_x = self.width // 2
        center_y = self.height // 2
        base_radius = min(self.width, self.height) // 4
        max_bar_length = min(self.width, self.height) // 3
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Draw bars radiating from center
        for i, magnitude in enumerate(normalized_bands):
            angle = (i / num_bands) * 2 * math.pi
            bar_length = magnitude * max_bar_length
            
            # Start point
            x1 = center_x + int(base_radius * math.cos(angle))
            y1 = center_y + int(base_radius * math.sin(angle))
            
            # End point
            x2 = center_x + int((base_radius + bar_length) * math.cos(angle))
            y2 = center_y + int((base_radius + bar_length) * math.sin(angle))
            
            color = self.get_color(i, num_bands, magnitude)
            
            # Draw line with width
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
        
        return img


class LineWaveformVisualizer(BaseVisualizer):
    """Traditional oscilloscope-style line waveform."""
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render line waveform."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_points = len(bands)
        if num_points < 2:
            return img
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Create waveform points
        points = []
        center_y = self.height // 2
        
        for i, magnitude in enumerate(normalized_bands):
            x = int((i / num_points) * self.width)
            # Alternate above and below center for waveform effect
            wave_height = int(magnitude * self.height * 0.4)
            if i % 2 == 0:
                y = center_y - wave_height
            else:
                y = center_y + wave_height
            points.append((x, y))
        
        # Draw line
        if len(points) >= 2:
            # Get average color
            avg_magnitude = np.mean(normalized_bands)
            color = self.get_color(num_points // 2, num_points, avg_magnitude)
            
            draw.line(points, fill=color, width=3)
        
        return img


class ParticleVisualizer(BaseVisualizer):
    """Particle system that reacts to audio."""
    
    def __init__(self, width: int, height: int, settings: Dict[str, Any]):
        """Initialize particle visualizer."""
        super().__init__(width, height, settings)
        self.particles = []
        self.max_particles = 200
    
    def render(self, bands: np.ndarray, spectrum_data: np.ndarray, 
               frame_number: int) -> Image.Image:
        """Render particle system."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        num_bands = len(bands)
        
        # Normalize bands
        if np.max(bands) > 0:
            normalized_bands = bands / np.max(bands)
        else:
            normalized_bands = bands
        
        # Generate new particles based on audio intensity
        for i, magnitude in enumerate(normalized_bands):
            if magnitude > 0.3 and len(self.particles) < self.max_particles:
                # Create particle
                x = int((i / num_bands) * self.width)
                y = self.height // 2
                
                # Random velocity based on magnitude
                vx = (np.random.random() - 0.5) * magnitude * 20
                vy = (np.random.random() - 0.5) * magnitude * 20
                
                color = self.get_color(i, num_bands, magnitude)
                
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': vx,
                    'vy': vy,
                    'life': 1.0,
                    'color': color,
                    'size': int(magnitude * 10) + 2
                })
        
        # Update and draw particles
        new_particles = []
        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Apply gravity
            particle['vy'] += 0.5
            
            # Reduce life
            particle['life'] -= 0.02
            
            # Keep particle if still alive and in bounds
            if particle['life'] > 0:
                # Draw particle
                x = int(particle['x'])
                y = int(particle['y'])
                size = particle['size']
                
                # Fade color based on life
                r, g, b, a = particle['color']
                a = int(255 * particle['life'])
                color = (r, g, b, a)
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
                    new_particles.append(particle)
        
        self.particles = new_particles
        
        return img


class VisualizerFactory:
    """Factory for creating visualizers."""
    
    @staticmethod
    def create(style: str, width: int, height: int, settings: Dict[str, Any]) -> BaseVisualizer:
        """
        Create visualizer instance.
        
        Args:
            style: Visualizer style name
            width: Image width
            height: Image height
            settings: Settings dictionary
            
        Returns:
            Visualizer instance
        """
        style = style.lower().replace(' ', '_')
        
        if style == 'bars':
            return BarsVisualizer(width, height, settings)
        elif style == 'filled_waveform':
            return FilledWaveformVisualizer(width, height, settings)
        elif style == 'circle':
            return CircleVisualizer(width, height, settings)
        elif style == 'line_waveform':
            return LineWaveformVisualizer(width, height, settings)
        elif style == 'particle':
            return ParticleVisualizer(width, height, settings)
        else:
            # Default to bars
            return BarsVisualizer(width, height, settings)
