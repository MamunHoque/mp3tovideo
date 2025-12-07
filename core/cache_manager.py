"""
Cache management module for MP3 Spectrum Visualizer.
Provides intelligent caching for computed data and resources.
"""

from typing import Any, Dict, Optional, Tuple
import numpy as np
from functools import lru_cache
import hashlib


class CacheManager:
    """Manages caching for expensive operations."""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self._spectrum_cache: Dict[int, np.ndarray] = {}
        self._bands_cache: Dict[Tuple[int, int], np.ndarray] = {}
        self._image_cache: Dict[str, Any] = {}
        self._access_count: Dict[str, int] = {}
    
    def cache_spectrum(self, frame_number: int, spectrum: np.ndarray) -> None:
        """
        Cache spectrum data for a frame.
        
        Args:
            frame_number: Frame number
            spectrum: Spectrum data
        """
        if len(self._spectrum_cache) >= self.max_size:
            # Remove least accessed item
            self._evict_lru(self._spectrum_cache)
        
        self._spectrum_cache[frame_number] = spectrum.copy()
        self._access_count[f'spectrum_{frame_number}'] = 0
    
    def get_spectrum(self, frame_number: int) -> Optional[np.ndarray]:
        """
        Get cached spectrum data.
        
        Args:
            frame_number: Frame number
            
        Returns:
            Spectrum data or None if not cached
        """
        key = f'spectrum_{frame_number}'
        if frame_number in self._spectrum_cache:
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._spectrum_cache[frame_number].copy()
        return None
    
    def cache_bands(self, frame_number: int, num_bands: int, bands: np.ndarray) -> None:
        """
        Cache frequency bands for a frame.
        
        Args:
            frame_number: Frame number
            num_bands: Number of bands
            bands: Band data
        """
        key = (frame_number, num_bands)
        
        if len(self._bands_cache) >= self.max_size:
            self._evict_lru(self._bands_cache)
        
        self._bands_cache[key] = bands.copy()
        self._access_count[f'bands_{frame_number}_{num_bands}'] = 0
    
    def get_bands(self, frame_number: int, num_bands: int) -> Optional[np.ndarray]:
        """
        Get cached frequency bands.
        
        Args:
            frame_number: Frame number
            num_bands: Number of bands
            
        Returns:
            Band data or None if not cached
        """
        key = (frame_number, num_bands)
        cache_key = f'bands_{frame_number}_{num_bands}'
        
        if key in self._bands_cache:
            self._access_count[cache_key] = self._access_count.get(cache_key, 0) + 1
            return self._bands_cache[key].copy()
        return None
    
    def cache_image(self, image_path: str, image: Any) -> None:
        """
        Cache an image.
        
        Args:
            image_path: Path to image (used as key)
            image: PIL Image object
        """
        if len(self._image_cache) >= self.max_size:
            self._evict_lru(self._image_cache)
        
        self._image_cache[image_path] = image.copy()
        self._access_count[f'image_{image_path}'] = 0
    
    def get_image(self, image_path: str) -> Optional[Any]:
        """
        Get cached image.
        
        Args:
            image_path: Path to image
            
        Returns:
            PIL Image or None if not cached
        """
        key = f'image_{image_path}'
        if image_path in self._image_cache:
            self._access_count[key] = self._access_count.get(key, 0) + 1
            return self._image_cache[image_path].copy()
        return None
    
    def _evict_lru(self, cache: Dict) -> None:
        """
        Evict least recently used item from cache.
        
        Args:
            cache: Cache dictionary to evict from
        """
        if not cache:
            return
        
        # Find least accessed item
        min_key = None
        min_count = float('inf')
        
        for key in cache.keys():
            # Create access key based on cache type
            if isinstance(key, tuple):
                access_key = f'bands_{key[0]}_{key[1]}'
            elif isinstance(key, int):
                access_key = f'spectrum_{key}'
            else:
                access_key = f'image_{key}'
            
            count = self._access_count.get(access_key, 0)
            if count < min_count:
                min_count = count
                min_key = key
        
        # Remove least accessed item
        if min_key is not None:
            del cache[min_key]
            # Clean up access count
            if isinstance(min_key, tuple):
                access_key = f'bands_{min_key[0]}_{min_key[1]}'
            elif isinstance(min_key, int):
                access_key = f'spectrum_{min_key}'
            else:
                access_key = f'image_{min_key}'
            self._access_count.pop(access_key, None)
    
    def clear(self) -> None:
        """Clear all caches."""
        self._spectrum_cache.clear()
        self._bands_cache.clear()
        self._image_cache.clear()
        self._access_count.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'spectrum_cached': len(self._spectrum_cache),
            'bands_cached': len(self._bands_cache),
            'images_cached': len(self._image_cache),
            'total_cached': len(self._spectrum_cache) + len(self._bands_cache) + len(self._image_cache)
        }

