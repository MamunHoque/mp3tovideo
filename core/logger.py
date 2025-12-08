"""
Centralized logging module for MP3 Spectrum Visualizer.
Provides structured logging with different levels.
"""

import logging
import sys
from typing import Optional, Callable
from pathlib import Path


class Logger:
    """Centralized logger for the application."""
    
    _instance: Optional['Logger'] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize logger."""
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = logging.getLogger('SpectrumVisualizer')
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # GUI handler callback (set by GUI)
        self.gui_handler_callback: Optional[Callable[[str, str], None]] = None
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info)
    
    def set_level(self, level: str) -> None:
        """
        Set logging level.
        
        Args:
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
    
    def add_file_handler(self, log_file: str) -> None:
        """
        Add file handler for logging to file.
        
        Args:
            log_file: Path to log file
        """
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def set_gui_handler(self, callback: Callable[[str, str], None]) -> None:
        """
        Set GUI handler callback for displaying logs in GUI.
        
        Args:
            callback: Function(level, message) to call for each log message
        """
        self.gui_handler_callback = callback
        
        # Add custom handler that uses the callback
        class GUIHandler(logging.Handler):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
                self.setLevel(logging.DEBUG)
            
            def emit(self, record):
                try:
                    level = record.levelname
                    msg = self.format(record)
                    if self.callback:
                        self.callback(level, msg)
                except Exception:
                    pass
        
        gui_handler = GUIHandler(callback)
        gui_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        gui_handler.setFormatter(gui_format)
        self.logger.addHandler(gui_handler)


# Global logger instance
_logger = Logger()


def get_logger() -> Logger:
    """Get the global logger instance."""
    return _logger



