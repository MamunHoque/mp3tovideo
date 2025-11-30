"""
Preview widget for displaying video preview frames with real-time playback.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image
import io
from typing import List, Optional


class PreviewWidget(QWidget):
    """Widget for displaying preview frames with real-time playback."""
    
    def __init__(self, parent=None):
        """
        Initialize preview widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.frames: List[Image.Image] = []
        self.current_frame_index = 0
        self.is_playing = False
        self.frame_rate = 30
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setText("Preview will appear here")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3e3e3e;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.preview_label)
        self.setLayout(layout)
    
    def set_frames(self, frames: List[Image.Image], frame_rate: int = 30):
        """
        Set frames for preview playback.
        
        Args:
            frames: List of PIL Images
            frame_rate: Frame rate for playback
        """
        self.frames = frames
        self.frame_rate = frame_rate
        self.current_frame_index = 0
        
        if self.frames:
            self.display_frame(self.frames[0])
            # Update timer interval based on frame rate
            interval = int(1000 / frame_rate)  # milliseconds
            self.timer.setInterval(interval)
    
    def play(self):
        """Start playing preview frames."""
        if self.frames and not self.is_playing:
            self.is_playing = True
            self.timer.start()
    
    def pause(self):
        """Pause preview playback."""
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
    
    def stop(self):
        """Stop preview playback and reset to first frame."""
        self.pause()
        self.current_frame_index = 0
        if self.frames:
            self.display_frame(self.frames[0])
    
    def next_frame(self):
        """Display next frame in sequence."""
        if not self.frames:
            return
        
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        self.display_frame(self.frames[self.current_frame_index])
    
    def is_playing_preview(self) -> bool:
        """Check if preview is currently playing."""
        return self.is_playing
    
    def display_frame(self, pil_image: Image.Image):
        """
        Display a PIL Image in the preview.
        
        Args:
            pil_image: PIL Image to display
        """
        if pil_image is None:
            return
        
        # Convert PIL Image to QPixmap
        try:
            # Resize to fit preview while maintaining aspect ratio
            preview_width = self.preview_label.width()
            preview_height = self.preview_label.height()
            
            if preview_width > 0 and preview_height > 0:
                # Calculate aspect ratio preserving size
                img_width, img_height = pil_image.size
                aspect_ratio = img_width / img_height
                
                if preview_width / preview_height > aspect_ratio:
                    display_height = preview_height
                    display_width = int(preview_height * aspect_ratio)
                else:
                    display_width = preview_width
                    display_height = int(preview_width / aspect_ratio)
                
                pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Create QImage from bytes
            qimage = QImage()
            qimage.loadFromData(img_bytes.read())
            
            # Convert to QPixmap and display
            pixmap = QPixmap.fromImage(qimage)
            self.preview_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error displaying frame: {e}")
    
    def clear_preview(self):
        """Clear the preview display."""
        self.preview_label.clear()
        self.preview_label.setText("Preview will appear here")
    
    def set_message(self, message: str):
        """
        Set a text message in the preview.
        
        Args:
            message: Message to display
        """
        self.preview_label.clear()
        self.preview_label.setText(message)

