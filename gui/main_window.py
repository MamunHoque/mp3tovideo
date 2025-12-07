"""
Main window for MP3 Spectrum Visualizer application.
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QSlider, QCheckBox, QComboBox, QLineEdit,
    QTextEdit, QGroupBox, QColorDialog, QProgressBar, QMessageBox,
    QScrollArea, QGridLayout, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

from gui.preview_widget import PreviewWidget
from core.audio_processor import AudioProcessor
from core.video_generator import VideoGenerator
from core.settings import SettingsManager


class VideoGenerationThread(QThread):
    """Thread for video generation to prevent GUI freezing."""
    
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, video_generator, output_path, preview_seconds=None):
        """
        Initialize video generation thread.
        
        Args:
            video_generator: VideoGenerator instance
            output_path: Output video path
            preview_seconds: Seconds to generate (None for full video)
        """
        super().__init__()
        self.video_generator = video_generator
        self.output_path = output_path
        self.preview_seconds = preview_seconds
    
    def run(self):
        """Run video generation."""
        try:
            def progress_callback(current, total):
                self.progress.emit(current, total)
            
            success = self.video_generator.generate_video(
                self.output_path,
                progress_callback=progress_callback,
                preview_seconds=self.preview_seconds
            )
            
            if success:
                self.finished.emit(True, f"Video generated successfully: {self.output_path}")
            else:
                self.finished.emit(False, "Error generating video. Check console for details.")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.settings_manager = SettingsManager()
        self.audio_processor = None
        self.video_generator = None
        self.generation_thread = None
        self.preview_frames = []
        self.preview_update_timer = QTimer()
        self.preview_update_timer.setSingleShot(True)
        self.preview_update_timer.timeout.connect(self.generate_preview_frames)
        self.auto_preview_enabled = True
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("MP3 Spectrum Visualizer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e3e;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3e3e3e;
                color: #ffffff;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4a9eff;
            }
            QTabBar::tab:hover {
                background-color: #5aaeff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3e3e3e;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QTextEdit {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a9eff;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5aaeff;
            }
            QPushButton:pressed {
                background-color: #3a8eef;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background: #3e3e3e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a9eff;
                border: 1px solid #3a8eef;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QComboBox {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 2px;
            }
        """)
        
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel: Tabbed Controls
        controls_panel = self.create_tabbed_controls()
        main_layout.addWidget(controls_panel, 1)
        
        # Right panel: File Selection, Output, and Preview
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_tabbed_controls(self) -> QWidget:
        """Create tabbed controls panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Background Tab
        bg_tab = self.create_background_tab()
        self.tabs.addTab(bg_tab, "Background")
        
        # Text Logo Tab
        text_logo_tab = self.create_text_logo_tab()
        self.tabs.addTab(text_logo_tab, "Text Logo")
        
        # Visualizer Tab
        visualizer_tab = self.create_visualizer_tab()
        self.tabs.addTab(visualizer_tab, "Visualizer")
        
        # Auto Lyrics Tab
        lyrics_tab = self.create_auto_lyrics_tab()
        self.tabs.addTab(lyrics_tab, "Auto Lyrics")
        
        # Performance Tab
        performance_tab = self.create_performance_tab()
        self.tabs.addTab(performance_tab, "Performance")
        
        # Save/Load Tab
        save_load_tab = self.create_save_load_tab()
        self.tabs.addTab(save_load_tab, "Save/Load")
        
        layout.addWidget(self.tabs)
        panel.setLayout(layout)
        return panel
    
    def create_background_tab(self) -> QWidget:
        """Create Background tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Background Type Selection
        bg_type_group = QGroupBox("Background Type")
        bg_type_layout = QVBoxLayout()
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["Image", "Video", "Solid Color"])
        self.bg_type_combo.currentTextChanged.connect(self.on_background_type_changed)
        bg_type_layout.addWidget(self.bg_type_combo)
        bg_type_group.setLayout(bg_type_layout)
        layout.addWidget(bg_type_group)
        
        # Background Image
        self.bg_image_group = QGroupBox("Background Image (Optional)")
        bg_layout = QVBoxLayout()
        
        bg_file_layout = QHBoxLayout()
        self.bg_path_input = QLineEdit()
        self.bg_path_input.setPlaceholderText("No background selected")
        self.bg_browse_btn = QPushButton("Browse Image...")
        self.bg_browse_btn.clicked.connect(self.browse_background)
        bg_file_layout.addWidget(self.bg_path_input, 1)
        bg_file_layout.addWidget(self.bg_browse_btn)
        bg_layout.addLayout(bg_file_layout)
        
        self.bg_image_group.setLayout(bg_layout)
        layout.addWidget(self.bg_image_group)
        
        # Background Video
        self.bg_video_group = QGroupBox("Background Video (Optional)")
        bg_video_layout = QVBoxLayout()
        
        bg_video_file_layout = QHBoxLayout()
        self.bg_video_path_input = QLineEdit()
        self.bg_video_path_input.setPlaceholderText("No video selected")
        self.bg_video_browse_btn = QPushButton("Browse Video...")
        self.bg_video_browse_btn.clicked.connect(self.browse_video_background)
        bg_video_file_layout.addWidget(self.bg_video_path_input, 1)
        bg_video_file_layout.addWidget(self.bg_video_browse_btn)
        bg_video_layout.addLayout(bg_video_file_layout)
        
        self.bg_video_group.setLayout(bg_video_layout)
        self.bg_video_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.bg_video_group)
        
        # Solid Color Background
        self.bg_color_group = QGroupBox("Background Color")
        bg_color_layout = QVBoxLayout()
        self.bg_color_btn = QPushButton("Choose Color...")
        self.bg_color_btn.clicked.connect(self.choose_background_color)
        bg_color_layout.addWidget(self.bg_color_btn)
        self.bg_color_group.setLayout(bg_color_layout)
        self.bg_color_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.bg_color_group)
        
        # Background Fit
        fit_group = QGroupBox("Background Fit")
        fit_layout = QVBoxLayout()
        self.bg_fit_combo = QComboBox()
        self.bg_fit_combo.addItems(["Stretch to Fit", "Tile", "Center"])
        self.bg_fit_combo.currentTextChanged.connect(self.update_settings)
        fit_layout.addWidget(self.bg_fit_combo)
        fit_group.setLayout(fit_layout)
        layout.addWidget(fit_group)
        
        # Background Blur
        blur_group = QGroupBox("Background Blur")
        blur_layout = QVBoxLayout()
        blur_slider_layout = QHBoxLayout()
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 100)
        self.blur_slider.setValue(0)
        self.blur_slider.valueChanged.connect(self.update_blur_label)
        self.blur_label = QLabel("0")
        self.blur_label.setMinimumWidth(40)
        blur_slider_layout.addWidget(self.blur_slider)
        blur_slider_layout.addWidget(self.blur_label)
        blur_layout.addLayout(blur_slider_layout)
        blur_group.setLayout(blur_layout)
        layout.addWidget(blur_group)
        
        # Black & White
        self.bw_checkbox = QCheckBox("Black White Background")
        self.bw_checkbox.stateChanged.connect(self.update_settings)
        layout.addWidget(self.bw_checkbox)
        
        # Vignette
        vignette_group = QGroupBox("Vignette Intensity")
        vignette_layout = QVBoxLayout()
        vignette_slider_layout = QHBoxLayout()
        self.vignette_slider = QSlider(Qt.Horizontal)
        self.vignette_slider.setRange(0, 100)
        self.vignette_slider.setValue(0)
        self.vignette_slider.valueChanged.connect(self.update_vignette_label)
        self.vignette_label = QLabel("0")
        self.vignette_label.setMinimumWidth(40)
        vignette_slider_layout.addWidget(self.vignette_slider)
        vignette_slider_layout.addWidget(self.vignette_label)
        vignette_layout.addLayout(vignette_slider_layout)
        vignette_group.setLayout(vignette_layout)
        layout.addWidget(vignette_group)
        
        # Club Strobe Effect
        strobe_group = QGroupBox("Club Strobe Effect")
        strobe_layout = QVBoxLayout()
        strobe_check_layout = QHBoxLayout()
        self.strobe_checkbox = QCheckBox("Enable Club Strobe Effect")
        self.strobe_checkbox.stateChanged.connect(self.toggle_strobe_color)
        strobe_check_layout.addWidget(self.strobe_checkbox)
        strobe_layout.addLayout(strobe_check_layout)
        
        self.strobe_color_btn = QPushButton("Strobe Color...")
        self.strobe_color_btn.setEnabled(False)
        self.strobe_color_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #00ff88;
            }
        """)
        self.strobe_color_btn.clicked.connect(self.choose_strobe_color)
        strobe_layout.addWidget(self.strobe_color_btn)
        strobe_group.setLayout(strobe_layout)
        layout.addWidget(strobe_group)
        
        # Background Animation
        anim_group = QGroupBox("Background Animation")
        anim_layout = QVBoxLayout()
        self.animation_combo = QComboBox()
        self.animation_combo.addItems(["None", "Fade In"])
        self.animation_combo.currentTextChanged.connect(self.update_settings)
        anim_layout.addWidget(self.animation_combo)
        anim_group.setLayout(anim_layout)
        layout.addWidget(anim_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_text_logo_tab(self) -> QWidget:
        """Create Text Logo tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Text Overlay
        text_group = QGroupBox("Text Overlay")
        text_layout = QVBoxLayout()
        self.text_overlay_input = QLineEdit()
        self.text_overlay_input.setPlaceholderText("Enter text to overlay...")
        self.text_overlay_input.textChanged.connect(self.update_settings)
        text_layout.addWidget(self.text_overlay_input)
        
        # Text Position
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position:"))
        self.text_position_combo = QComboBox()
        self.text_position_combo.addItems(["Center", "Top", "Bottom"])
        self.text_position_combo.currentTextChanged.connect(self.update_settings)
        position_layout.addWidget(self.text_position_combo)
        text_layout.addLayout(position_layout)
        
        # Text Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.text_color_btn = QPushButton("Choose Color...")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        color_layout.addWidget(self.text_color_btn)
        text_layout.addLayout(color_layout)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # Logo
        logo_group = QGroupBox("Logo")
        logo_layout = QVBoxLayout()
        logo_file_layout = QHBoxLayout()
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setPlaceholderText("No logo selected")
        self.logo_browse_btn = QPushButton("Browse...")
        self.logo_browse_btn.clicked.connect(self.browse_logo)
        logo_file_layout.addWidget(self.logo_path_input, 1)
        logo_file_layout.addWidget(self.logo_browse_btn)
        logo_layout.addLayout(logo_file_layout)
        logo_group.setLayout(logo_layout)
        layout.addWidget(logo_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_visualizer_tab(self) -> QWidget:
        """Create Visualizer tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Enable Visualizer
        self.visualizer_enabled_checkbox = QCheckBox("Enable Visualizer")
        self.visualizer_enabled_checkbox.setChecked(True)
        self.visualizer_enabled_checkbox.stateChanged.connect(self.toggle_visualizer_settings)
        layout.addWidget(self.visualizer_enabled_checkbox)
        
        # Visualizer Style
        style_group = QGroupBox("Visualizer Style")
        style_layout = QVBoxLayout()
        self.visualizer_style_combo = QComboBox()
        self.visualizer_style_combo.addItems([
            "Filled Waveform",
            "Bars",
            "Circle",
            "Line Waveform",
            "Particle"
        ])
        self.visualizer_style_combo.setCurrentText("Filled Waveform")
        self.visualizer_style_combo.currentTextChanged.connect(self.update_settings)
        style_layout.addWidget(self.visualizer_style_combo)
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Color Gradient
        gradient_group = QGroupBox("Color Gradient")
        gradient_layout = QVBoxLayout()
        self.color_gradient_combo = QComboBox()
        self.color_gradient_combo.addItems([
            "Pitch Rainbow",
            "Frequency-based",
            "Energy-based",
            "Custom",
            "Monochrome"
        ])
        self.color_gradient_combo.setCurrentText("Pitch Rainbow")
        self.color_gradient_combo.currentTextChanged.connect(self.update_settings)
        gradient_layout.addWidget(self.color_gradient_combo)
        gradient_group.setLayout(gradient_layout)
        layout.addWidget(gradient_group)
        
        # Orientation
        orientation_group = QGroupBox("Orientation")
        orientation_layout = QVBoxLayout()
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems([
            "Landscape (16:9)",
            "Portrait (9:16)",
            "Square (1:1)",
            "Ultrawide (21:9)",
            "Custom"
        ])
        self.orientation_combo.setCurrentText("Landscape (16:9)")
        self.orientation_combo.currentTextChanged.connect(self.update_orientation)
        orientation_layout.addWidget(self.orientation_combo)
        orientation_group.setLayout(orientation_layout)
        layout.addWidget(orientation_group)
        
        # Resolution
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QVBoxLayout()
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1080p (Full HD)",
            "720p (HD)",
            "4K (2160p)",
            "1440p (2K)",
            "480p (SD)",
            "Custom"
        ])
        self.resolution_combo.setCurrentText("1080p (Full HD)")
        self.resolution_combo.currentTextChanged.connect(self.update_resolution)
        resolution_layout.addWidget(self.resolution_combo)
        resolution_group.setLayout(resolution_layout)
        layout.addWidget(resolution_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_performance_tab(self) -> QWidget:
        """Create Performance tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Info label
        info_label = QLabel("⚡ Optimize video generation speed")
        info_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #4a9eff;")
        layout.addWidget(info_label)
        
        # Quality Preset
        quality_group = QGroupBox("Quality Preset")
        quality_layout = QVBoxLayout()
        
        self.quality_preset_combo = QComboBox()
        self.quality_preset_combo.addItems(["Fast (Lower Quality)", "Balanced", "High Quality (Slower)"])
        self.quality_preset_combo.setCurrentText("Fast (Lower Quality)")
        self.quality_preset_combo.currentTextChanged.connect(self.on_quality_preset_changed)
        quality_layout.addWidget(self.quality_preset_combo)
        
        quality_info = QLabel("Fast: ~2-3x faster, good for previews\nBalanced: Good quality/speed ratio\nHigh: Best quality, slowest")
        quality_info.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        quality_layout.addWidget(quality_info)
        
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)
        
        # Encoding Preset
        encoding_group = QGroupBox("Encoding Speed")
        encoding_layout = QVBoxLayout()
        
        self.encoding_preset_combo = QComboBox()
        self.encoding_preset_combo.addItems(["Ultrafast", "Fast", "Medium", "Slow"])
        self.encoding_preset_combo.setCurrentText("Ultrafast")
        self.encoding_preset_combo.currentTextChanged.connect(self.update_settings)
        encoding_layout.addWidget(self.encoding_preset_combo)
        
        encoding_info = QLabel("Ultrafast: Fastest encoding, larger file size\nSlow: Slower encoding, smaller file size")
        encoding_info.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        encoding_layout.addWidget(encoding_info)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
        # Hardware Acceleration
        hw_accel_group = QGroupBox("Hardware Acceleration")
        hw_accel_layout = QVBoxLayout()
        
        self.hw_accel_checkbox = QCheckBox("Use Hardware Acceleration (macOS VideoToolbox)")
        self.hw_accel_checkbox.setChecked(True)
        self.hw_accel_checkbox.stateChanged.connect(self.update_settings)
        hw_accel_layout.addWidget(self.hw_accel_checkbox)
        
        hw_info = QLabel("Significantly faster on supported Macs.\nAutomatically falls back to software if unavailable.")
        hw_info.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        hw_accel_layout.addWidget(hw_info)
        
        hw_accel_group.setLayout(hw_accel_layout)
        layout.addWidget(hw_accel_group)
        
        # Resolution Quick Settings
        quick_res_group = QGroupBox("Quick Resolution")
        quick_res_layout = QVBoxLayout()
        
        quick_res_info = QLabel("Lower resolution = faster generation")
        quick_res_info.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        quick_res_layout.addWidget(quick_res_info)
        
        quick_res_buttons = QHBoxLayout()
        
        res_720_btn = QPushButton("720p")
        res_720_btn.clicked.connect(lambda: self.set_quick_resolution(1280, 720))
        quick_res_buttons.addWidget(res_720_btn)
        
        res_1080_btn = QPushButton("1080p")
        res_1080_btn.clicked.connect(lambda: self.set_quick_resolution(1920, 1080))
        quick_res_buttons.addWidget(res_1080_btn)
        
        quick_res_layout.addLayout(quick_res_buttons)
        quick_res_group.setLayout(quick_res_layout)
        layout.addWidget(quick_res_group)
        
        # Performance Tips
        tips_group = QGroupBox("💡 Performance Tips")
        tips_layout = QVBoxLayout()
        
        tips_text = QLabel(
            "• Use 'Fast' preset for quick previews\n"
            "• Lower resolution (720p) = 2x faster\n"
            "• Disable beat sync if not needed\n"
            "• Use solid color background instead of video\n"
            "• Disable blur/vignette effects"
        )
        tips_text.setStyleSheet("color: #cccccc; font-size: 11px;")
        tips_text.setWordWrap(True)
        tips_layout.addWidget(tips_text)
        
        tips_group.setLayout(tips_layout)
        layout.addWidget(tips_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_auto_lyrics_tab(self) -> QWidget:
        """Create Auto Lyrics tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Auto Lyrics
        lyrics_group = QGroupBox("Auto Lyrics")
        lyrics_layout = QVBoxLayout()
        
        self.auto_lyrics_checkbox = QCheckBox("Enable Auto Lyrics")
        self.auto_lyrics_checkbox.stateChanged.connect(self.toggle_lyrics_input)
        lyrics_layout.addWidget(self.auto_lyrics_checkbox)
        
        lyrics_layout.addWidget(QLabel("Lyrics Text:"))
        self.lyrics_text = QTextEdit()
        self.lyrics_text.setPlaceholderText("Enter lyrics here...")
        self.lyrics_text.setMinimumHeight(200)
        self.lyrics_text.setEnabled(False)
        self.lyrics_text.textChanged.connect(self.update_settings)
        lyrics_layout.addWidget(self.lyrics_text)
        
        lyrics_group.setLayout(lyrics_layout)
        layout.addWidget(lyrics_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_save_load_tab(self) -> QWidget:
        """Create Save/Load tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Save/Load Settings
        settings_group = QGroupBox("Settings Management")
        settings_layout = QVBoxLayout()
        
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(self.save_settings_btn)
        
        self.load_settings_btn = QPushButton("Load Settings")
        self.load_settings_btn.clicked.connect(self.load_settings)
        settings_layout.addWidget(self.load_settings_btn)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with file selection, output, and preview."""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # MP3 File Selection
        mp3_group = QGroupBox("MP3 File")
        mp3_layout = QVBoxLayout()
        mp3_file_layout = QHBoxLayout()
        self.mp3_path_input = QLineEdit()
        self.mp3_path_input.setPlaceholderText("No MP3 file selected")
        self.mp3_browse_btn = QPushButton("Browse...")
        self.mp3_browse_btn.clicked.connect(self.browse_mp3)
        mp3_file_layout.addWidget(self.mp3_path_input, 1)
        mp3_file_layout.addWidget(self.mp3_browse_btn)
        mp3_layout.addLayout(mp3_file_layout)
        mp3_group.setLayout(mp3_layout)
        layout.addWidget(mp3_group)
        
        # Output Video
        output_group = QGroupBox("Output Video")
        output_layout = QVBoxLayout()
        output_file_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output path...")
        self.output_browse_btn = QPushButton("Save As...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        output_file_layout.addWidget(self.output_path_input, 1)
        output_file_layout.addWidget(self.output_browse_btn)
        output_layout.addLayout(output_file_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Preview
        preview_group = QGroupBox("Video Preview")
        preview_layout = QVBoxLayout()
        self.preview_widget = PreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        # Preview Controls
        preview_controls_layout = QHBoxLayout()
        self.play_preview_btn = QPushButton("▶ Play")
        self.play_preview_btn.clicked.connect(self.toggle_preview_playback)
        self.play_preview_btn.setEnabled(False)
        preview_controls_layout.addWidget(self.play_preview_btn)
        
        self.auto_preview_checkbox = QCheckBox("Auto Update")
        self.auto_preview_checkbox.setChecked(True)
        self.auto_preview_checkbox.stateChanged.connect(self.toggle_auto_preview)
        preview_controls_layout.addWidget(self.auto_preview_checkbox)
        
        preview_layout.addLayout(preview_controls_layout)
        
        # Generate Preview Video Button (for file export)
        self.preview_btn = QPushButton("▶ Generate Preview Video")
        self.preview_btn.clicked.connect(self.generate_preview)
        preview_layout.addWidget(self.preview_btn)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group, 1)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        # Generate Video Button
        self.generate_btn = QPushButton("🚀 Generate Video")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                font-size: 14px;
                padding: 12px;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_video)
        layout.addWidget(self.generate_btn)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def choose_text_color(self):
        """Choose text overlay color."""
        current_color = self.settings_manager.get_setting('text_color', [255, 255, 255])
        color = QColorDialog.getColor(
            QColor(*current_color), self, "Choose Text Color"
        )
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            self.settings_manager.set_setting('text_color', rgb)
            self.update_settings()
    
    def create_controls_panel_OLD(self) -> QWidget:
        """Create controls panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # File Selection Section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # MP3 File
        mp3_layout = QHBoxLayout()
        self.mp3_path_label = QLabel("No MP3 file selected")
        self.mp3_browse_btn = QPushButton("Browse MP3...")
        self.mp3_browse_btn.clicked.connect(self.browse_mp3)
        mp3_layout.addWidget(self.mp3_path_label, 1)
        mp3_layout.addWidget(self.mp3_browse_btn)
        file_layout.addLayout(mp3_layout)
        
        # Background Image
        bg_layout = QHBoxLayout()
        self.bg_path_label = QLabel("No background selected")
        self.bg_browse_btn = QPushButton("Browse Background...")
        self.bg_browse_btn.clicked.connect(self.browse_background)
        bg_layout.addWidget(self.bg_path_label, 1)
        bg_layout.addWidget(self.bg_browse_btn)
        file_layout.addLayout(bg_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Background Customization Section
        bg_custom_group = QGroupBox("Background Customization")
        bg_custom_layout = QVBoxLayout()
        
        # Background Fit
        fit_layout = QHBoxLayout()
        fit_layout.addWidget(QLabel("Background Fit:"))
        self.bg_fit_combo = QComboBox()
        self.bg_fit_combo.addItems(["Stretch", "Tile", "Center"])
        self.bg_fit_combo.currentTextChanged.connect(self.update_settings)
        fit_layout.addWidget(self.bg_fit_combo)
        bg_custom_layout.addLayout(fit_layout)
        
        # Background Blur
        blur_layout = QHBoxLayout()
        blur_layout.addWidget(QLabel("Blur:"))
        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 100)
        self.blur_slider.setValue(0)
        self.blur_slider.valueChanged.connect(self.update_blur_label)
        self.blur_label = QLabel("0")
        self.blur_label.setMinimumWidth(30)
        blur_layout.addWidget(self.blur_slider)
        blur_layout.addWidget(self.blur_label)
        bg_custom_layout.addLayout(blur_layout)
        
        # Black & White
        self.bw_checkbox = QCheckBox("Black & White Background")
        self.bw_checkbox.stateChanged.connect(self.update_settings)
        bg_custom_layout.addWidget(self.bw_checkbox)
        
        # Vignette
        vignette_layout = QHBoxLayout()
        vignette_layout.addWidget(QLabel("Vignette:"))
        self.vignette_slider = QSlider(Qt.Horizontal)
        self.vignette_slider.setRange(0, 100)
        self.vignette_slider.setValue(0)
        self.vignette_slider.valueChanged.connect(self.update_vignette_label)
        self.vignette_label = QLabel("0")
        self.vignette_label.setMinimumWidth(30)
        vignette_layout.addWidget(self.vignette_slider)
        vignette_layout.addWidget(self.vignette_label)
        bg_custom_layout.addLayout(vignette_layout)
        
        bg_custom_group.setLayout(bg_custom_layout)
        layout.addWidget(bg_custom_group)
        
        # Visual Effects Section
        effects_group = QGroupBox("Visual Effects")
        effects_layout = QVBoxLayout()
        
        # Club Strobe
        strobe_layout = QHBoxLayout()
        self.strobe_checkbox = QCheckBox("Club Strobe Effect")
        self.strobe_checkbox.stateChanged.connect(self.toggle_strobe_color)
        strobe_layout.addWidget(self.strobe_checkbox)
        self.strobe_color_btn = QPushButton("Strobe Color")
        self.strobe_color_btn.setEnabled(False)
        self.strobe_color_btn.clicked.connect(self.choose_strobe_color)
        strobe_layout.addWidget(self.strobe_color_btn)
        effects_layout.addLayout(strobe_layout)
        
        # Background Animation
        anim_layout = QHBoxLayout()
        anim_layout.addWidget(QLabel("Background Animation:"))
        self.animation_combo = QComboBox()
        self.animation_combo.addItems(["None", "Fade In"])
        self.animation_combo.currentTextChanged.connect(self.update_settings)
        anim_layout.addWidget(self.animation_combo)
        effects_layout.addLayout(anim_layout)
        
        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)
        
        # Additional Features Section
        additional_group = QGroupBox("Additional Features")
        additional_layout = QVBoxLayout()
        
        # Auto Lyrics
        lyrics_layout = QHBoxLayout()
        self.auto_lyrics_checkbox = QCheckBox("Auto Lyrics")
        self.auto_lyrics_checkbox.stateChanged.connect(self.toggle_lyrics_input)
        lyrics_layout.addWidget(self.auto_lyrics_checkbox)
        additional_layout.addLayout(lyrics_layout)
        
        # Lyrics Text
        self.lyrics_text = QTextEdit()
        self.lyrics_text.setPlaceholderText("Enter lyrics here...")
        self.lyrics_text.setMaximumHeight(100)
        self.lyrics_text.setEnabled(False)
        self.lyrics_text.textChanged.connect(self.update_settings)
        additional_layout.addWidget(QLabel("Lyrics:"))
        additional_layout.addWidget(self.lyrics_text)
        
        # Logo
        logo_layout = QHBoxLayout()
        self.logo_path_label = QLabel("No logo selected")
        self.logo_browse_btn = QPushButton("Add Logo...")
        self.logo_browse_btn.clicked.connect(self.browse_logo)
        logo_layout.addWidget(self.logo_path_label, 1)
        logo_layout.addWidget(self.logo_browse_btn)
        additional_layout.addLayout(logo_layout)
        
        # Text Overlay
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text Overlay:"))
        self.text_overlay_input = QLineEdit()
        self.text_overlay_input.setPlaceholderText("Enter text to overlay...")
        self.text_overlay_input.textChanged.connect(self.update_settings)
        text_layout.addWidget(self.text_overlay_input)
        additional_layout.addLayout(text_layout)
        
        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        
        # Output Settings Section
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()
        
        # Output Path
        output_path_layout = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output path...")
        self.output_browse_btn = QPushButton("Browse...")
        self.output_browse_btn.clicked.connect(self.browse_output)
        output_path_layout.addWidget(self.output_path_input, 1)
        output_path_layout.addWidget(self.output_browse_btn)
        output_layout.addLayout(output_path_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self.generate_preview)
        self.generate_btn = QPushButton("Generate Video")
        self.generate_btn.clicked.connect(self.generate_video)
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.generate_btn)
        output_layout.addLayout(button_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        output_layout.addWidget(self.progress_bar)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Save/Load Settings
        settings_layout = QHBoxLayout()
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        self.load_settings_btn = QPushButton("Load Settings")
        self.load_settings_btn.clicked.connect(self.load_settings)
        settings_layout.addWidget(self.save_settings_btn)
        settings_layout.addWidget(self.load_settings_btn)
        layout.addLayout(settings_layout)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_preview_panel(self) -> QWidget:
        """Create preview panel."""
        panel = QWidget()
        layout = QVBoxLayout()
        
        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(preview_label)
        
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)
        
        panel.setLayout(layout)
        return panel
    
    def browse_mp3(self):
        """Browse for MP3 file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select MP3 File", "", "MP3 Files (*.mp3);;All Files (*)"
        )
        if file_path:
            self.mp3_path_input.setText(file_path)
            self.settings_manager.set_setting('mp3_path', file_path)
            self.load_audio()
    
    def browse_background(self):
        """Browse for background image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            self.bg_path_input.setText(file_path)
            self.settings_manager.set_setting('background_path', file_path)
            self.settings_manager.set_setting('video_background_path', '')  # Clear video background
            self.update_preview_frame()
    
    def browse_video_background(self):
        """Browse for background video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Background Video", "", 
            "Video Files (*.mp4);;All Files (*)"
        )
        if file_path:
            self.bg_video_path_input.setText(file_path)
            self.settings_manager.set_setting('video_background_path', file_path)
            self.settings_manager.set_setting('background_path', '')  # Clear image background
            self.update_preview_frame()
    
    def on_background_type_changed(self, bg_type: str):
        """Handle background type change."""
        if bg_type == "Image":
            self.bg_image_group.setVisible(True)
            self.bg_video_group.setVisible(False)
            self.bg_color_group.setVisible(False)
        elif bg_type == "Video":
            self.bg_image_group.setVisible(False)
            self.bg_video_group.setVisible(True)
            self.bg_color_group.setVisible(False)
        elif bg_type == "Solid Color":
            self.bg_image_group.setVisible(False)
            self.bg_video_group.setVisible(False)
            self.bg_color_group.setVisible(True)
        self.update_settings()
    
    def choose_background_color(self):
        """Choose solid background color."""
        current_color = self.settings_manager.get_setting('background_color', [0, 0, 0])
        color = QColorDialog.getColor(
            QColor(*current_color), self, "Choose Background Color"
        )
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            self.settings_manager.set_setting('background_color', rgb)
            self.update_settings()
    
    def browse_logo(self):
        """Browse for logo image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            self.logo_path_input.setText(file_path)
            self.settings_manager.set_setting('logo_path', file_path)
            self.update_preview_frame()
    
    def browse_output(self):
        """Browse for output file path."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Video As", "", "MP4 Files (*.mp4);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith('.mp4'):
                file_path += '.mp4'
            self.output_path_input.setText(file_path)
            self.settings_manager.set_setting('output_path', file_path)
    
    def load_audio(self):
        """Load audio file."""
        mp3_path = self.settings_manager.get_setting('mp3_path')
        if mp3_path and os.path.exists(mp3_path):
            try:
                self.audio_processor = AudioProcessor(mp3_path)
                self.audio_processor.load_audio()
                duration = self.audio_processor.get_duration()
                self.statusBar().showMessage(f"Audio loaded: {duration:.2f} seconds")
                self.update_video_generator()
                # Generate preview frames when audio is loaded
                if self.auto_preview_enabled:
                    self.generate_preview_frames()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load audio: {str(e)}")
    
    def update_video_generator(self):
        """Update video generator with current settings."""
        if self.audio_processor:
            settings = self.settings_manager.settings.copy()
            self.video_generator = VideoGenerator(self.audio_processor, settings)
    
    def update_blur_label(self, value):
        """Update blur label."""
        self.blur_label.setText(str(value))
        self.update_settings()
    
    def update_vignette_label(self, value):
        """Update vignette label."""
        self.vignette_label.setText(str(value))
        self.update_settings()
    
    def toggle_strobe_color(self, state):
        """Toggle strobe color button."""
        enabled = state == Qt.Checked
        self.strobe_color_btn.setEnabled(enabled)
        self.update_settings()
    
    def toggle_lyrics_input(self, state):
        """Toggle lyrics input."""
        enabled = state == Qt.Checked
        self.lyrics_text.setEnabled(enabled)
        self.update_settings()
    
    def toggle_visualizer_settings(self, state):
        """Toggle visualizer settings enabled state."""
        enabled = state == Qt.Checked
        # Enable/disable visualizer controls
        self.visualizer_style_combo.setEnabled(enabled)
        self.color_gradient_combo.setEnabled(enabled)
        self.orientation_combo.setEnabled(enabled)
        self.resolution_combo.setEnabled(enabled)
        self.update_settings()
    
    def on_quality_preset_changed(self, text):
        """Handle quality preset change."""
        if "Fast" in text:
            self.settings_manager.set_setting('quality_preset', 'fast')
            self.encoding_preset_combo.setCurrentText("Ultrafast")
        elif "Balanced" in text:
            self.settings_manager.set_setting('quality_preset', 'balanced')
            self.encoding_preset_combo.setCurrentText("Fast")
        elif "High" in text:
            self.settings_manager.set_setting('quality_preset', 'high')
            self.encoding_preset_combo.setCurrentText("Medium")
        self.update_settings()
    
    def set_quick_resolution(self, width, height):
        """Set resolution quickly."""
        self.settings_manager.set_setting('video_width', width)
        self.settings_manager.set_setting('video_height', height)
        self.update_video_generator()
        self.statusBar().showMessage(f"Resolution set to {width}x{height}")
    
    def update_orientation(self, orientation_text):
        """Update video dimensions based on orientation selection."""
        self.update_settings()
        # Update resolution based on orientation
        if orientation_text == "Landscape (16:9)":
            if self.resolution_combo.currentText() == "1080p (Full HD)":
                self.settings_manager.set_setting('video_width', 1920)
                self.settings_manager.set_setting('video_height', 1080)
            elif self.resolution_combo.currentText() == "720p (HD)":
                self.settings_manager.set_setting('video_width', 1280)
                self.settings_manager.set_setting('video_height', 720)
            elif self.resolution_combo.currentText() == "4K (2160p)":
                self.settings_manager.set_setting('video_width', 3840)
                self.settings_manager.set_setting('video_height', 2160)
        elif orientation_text == "Portrait (9:16)":
            if self.resolution_combo.currentText() == "1080p (Full HD)":
                self.settings_manager.set_setting('video_width', 1080)
                self.settings_manager.set_setting('video_height', 1920)
            elif self.resolution_combo.currentText() == "720p (HD)":
                self.settings_manager.set_setting('video_width', 720)
                self.settings_manager.set_setting('video_height', 1280)
        elif orientation_text == "Square (1:1)":
            if self.resolution_combo.currentText() == "1080p (Full HD)":
                self.settings_manager.set_setting('video_width', 1080)
                self.settings_manager.set_setting('video_height', 1080)
            elif self.resolution_combo.currentText() == "720p (HD)":
                self.settings_manager.set_setting('video_width', 720)
                self.settings_manager.set_setting('video_height', 720)
        self.update_video_generator()
    
    def update_resolution(self, resolution_text):
        """Update video dimensions based on resolution selection."""
        self.update_settings()
        orientation = self.orientation_combo.currentText()
        
        # Map resolution to dimensions
        resolution_map = {
            "1080p (Full HD)": 1080,
            "720p (HD)": 720,
            "4K (2160p)": 2160,
            "1440p (2K)": 1440,
            "480p (SD)": 480
        }
        
        height = resolution_map.get(resolution_text, 1080)
        
        if orientation == "Landscape (16:9)":
            width = int(height * 16 / 9)
        elif orientation == "Portrait (9:16)":
            width = int(height * 9 / 16)
        elif orientation == "Square (1:1)":
            width = height
        elif orientation == "Ultrawide (21:9)":
            width = int(height * 21 / 9)
        else:
            width = int(height * 16 / 9)  # Default to 16:9
        
        self.settings_manager.set_setting('video_width', width)
        self.settings_manager.set_setting('video_height', height)
        self.update_video_generator()
    
    def choose_strobe_color(self):
        """Choose strobe color."""
        current_color = self.settings_manager.get_setting('strobe_color', [255, 255, 255])
        color = QColorDialog.getColor(
            QColor(*current_color), self, "Choose Strobe Color"
        )
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            self.settings_manager.set_setting('strobe_color', rgb)
            self.update_settings()
    
    def update_settings(self):
        """Update settings from UI controls."""
        # Background type
        if hasattr(self, 'bg_type_combo'):
            bg_type = self.bg_type_combo.currentText().lower().replace(' ', '_')
            self.settings_manager.set_setting('background_type', bg_type)
        
        # Background settings
        fit_text = self.bg_fit_combo.currentText().lower()
        if 'stretch' in fit_text:
            fit_text = 'stretch'
        self.settings_manager.set_setting('background_fit', fit_text)
        self.settings_manager.set_setting('background_blur', 
                                        self.blur_slider.value())
        self.settings_manager.set_setting('background_bw', 
                                        self.bw_checkbox.isChecked())
        self.settings_manager.set_setting('vignette_intensity', 
                                        self.vignette_slider.value())
        
        # Effects settings
        self.settings_manager.set_setting('strobe_enabled', 
                                        self.strobe_checkbox.isChecked())
        animation_text = self.animation_combo.currentText().lower().replace(' ', '_')
        self.settings_manager.set_setting('background_animation', animation_text)
        
        # Additional features
        self.settings_manager.set_setting('auto_lyrics', 
                                        self.auto_lyrics_checkbox.isChecked())
        self.settings_manager.set_setting('lyrics_text', 
                                        self.lyrics_text.toPlainText())
        self.settings_manager.set_setting('text_overlay', 
                                        self.text_overlay_input.text())
        self.settings_manager.set_setting('text_position', 
                                        self.text_position_combo.currentText().lower())
        
        # Visualizer settings
        if hasattr(self, 'visualizer_enabled_checkbox'):
            self.settings_manager.set_setting('visualizer_enabled', 
                                            self.visualizer_enabled_checkbox.isChecked())
        if hasattr(self, 'visualizer_style_combo'):
            style_text = self.visualizer_style_combo.currentText().lower().replace(' ', '_')
            self.settings_manager.set_setting('visualizer_style', style_text)
        if hasattr(self, 'color_gradient_combo'):
            gradient_text = self.color_gradient_combo.currentText().lower().replace(' ', '_')
            self.settings_manager.set_setting('color_gradient', gradient_text)
        if hasattr(self, 'orientation_combo'):
            orientation_text = self.orientation_combo.currentText().lower().replace(' ', '_').replace('(', '').replace(')', '')
            self.settings_manager.set_setting('orientation', orientation_text)
        if hasattr(self, 'resolution_combo'):
            resolution_text = self.resolution_combo.currentText().split(' ')[0].lower()
            self.settings_manager.set_setting('resolution', resolution_text)
        
        # Performance settings
        if hasattr(self, 'hw_accel_checkbox'):
            self.settings_manager.set_setting('use_hardware_acceleration',
                                            self.hw_accel_checkbox.isChecked())
        if hasattr(self, 'encoding_preset_combo'):
            encoding_text = self.encoding_preset_combo.currentText().lower()
            self.settings_manager.set_setting('encoding_preset', encoding_text)
        
        # Update video generator
        self.update_video_generator()
        
        # Trigger preview update if auto-preview is enabled
        if self.auto_preview_enabled:
            # Stop current preview playback if playing
            if self.preview_widget.is_playing_preview():
                self.preview_widget.pause()
                self.play_preview_btn.setText("▶ Play")
            
            # Use a timer to debounce rapid setting changes
            self.preview_update_timer.stop()
            self.preview_update_timer.start(500)  # Wait 500ms after last change
    
    def toggle_auto_preview(self, state):
        """Toggle auto-preview updates."""
        self.auto_preview_enabled = state == Qt.Checked
        if self.auto_preview_enabled:
            self.generate_preview_frames()
    
    def generate_preview_frames(self):
        """Generate preview frames for real-time playback."""
        if not self.audio_processor or not self.video_generator:
            return
        
        try:
            # Generate 5 seconds of preview frames (or less if audio is shorter)
            frame_rate = self.settings_manager.get_setting('frame_rate', 30)
            duration = min(5.0, self.audio_processor.get_duration())
            num_frames = int(duration * frame_rate)
            
            # Limit to reasonable number of frames for performance
            max_preview_frames = 150  # ~5 seconds at 30fps
            num_frames = min(num_frames, max_preview_frames)
            
            self.preview_frames = []
            was_playing = self.preview_widget.is_playing_preview()
            
            # Generate frames in a separate thread to avoid blocking UI
            class PreviewFrameGenerator(QThread):
                frames_ready = pyqtSignal(list, int)
                
                def __init__(self, video_generator, num_frames, frame_rate):
                    super().__init__()
                    self.video_generator = video_generator
                    self.num_frames = num_frames
                    self.frame_rate = frame_rate
                
                def run(self):
                    frames = []
                    for i in range(self.num_frames):
                        try:
                            frame = self.video_generator.generate_frame(i)
                            frames.append(frame)
                        except Exception as e:
                            print(f"Error generating preview frame {i}: {e}")
                            break
                    self.frames_ready.emit(frames, self.frame_rate)
            
            self.preview_generator_thread = PreviewFrameGenerator(
                self.video_generator, num_frames, frame_rate
            )
            self.preview_generator_thread.frames_ready.connect(
                lambda frames, fr: self.on_preview_frames_ready(frames, fr, was_playing)
            )
            self.preview_generator_thread.start()
            
        except Exception as e:
            print(f"Error generating preview frames: {e}")
    
    def on_preview_frames_ready(self, frames, frame_rate, was_playing):
        """Handle preview frames ready signal."""
        self.preview_frames = frames
        if frames:
            self.preview_widget.set_frames(frames, frame_rate)
            self.play_preview_btn.setEnabled(True)
            if was_playing:
                self.preview_widget.play()
                self.play_preview_btn.setText("⏸ Pause")
    
    def toggle_preview_playback(self):
        """Toggle preview playback on/off."""
        if self.preview_widget.is_playing_preview():
            self.preview_widget.pause()
            self.play_preview_btn.setText("▶ Play")
        else:
            if not self.preview_frames:
                # Generate frames if not available
                self.generate_preview_frames()
            else:
                self.preview_widget.play()
                self.play_preview_btn.setText("⏸ Pause")
    
    def update_preview_frame(self):
        """Update preview with current frame (legacy method for compatibility)."""
        if self.video_generator:
            try:
                frame = self.video_generator.generate_frame(0)
                self.preview_widget.display_frame(frame)
            except Exception as e:
                print(f"Error updating preview: {e}")
    
    def generate_preview(self):
        """Generate preview video."""
        if not self.audio_processor:
            QMessageBox.warning(self, "Warning", "Please select an MP3 file first.")
            return
        
        if not self.output_path_input.text():
            QMessageBox.warning(self, "Warning", "Please select an output path first.")
            return
        
        self.update_settings()
        output_path = self.output_path_input.text()
        preview_path = output_path.replace('.mp4', '_preview.mp4')
        
        self.preview_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.generation_thread = VideoGenerationThread(
            self.video_generator, preview_path, preview_seconds=5
        )
        self.generation_thread.progress.connect(self.update_progress)
        self.generation_thread.finished.connect(self.on_preview_finished)
        self.generation_thread.start()
    
    def generate_video(self):
        """Generate full video."""
        if not self.audio_processor:
            QMessageBox.warning(self, "Warning", "Please select an MP3 file first.")
            return
        
        output_path = self.output_path_input.text()
        if not output_path:
            QMessageBox.warning(self, "Warning", "Please select an output path first.")
            return
        
        self.update_settings()
        
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.generation_thread = VideoGenerationThread(
            self.video_generator, output_path
        )
        self.generation_thread.progress.connect(self.update_progress)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.start()
    
    def update_progress(self, current, total):
        """Update progress bar."""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.statusBar().showMessage(f"Progress: {progress}%")
    
    def on_preview_finished(self, success, message):
        """Handle preview generation finished."""
        self.preview_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.statusBar().showMessage(message)
            QMessageBox.information(self, "Preview Complete", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def on_generation_finished(self, success, message):
        """Handle video generation finished."""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if success:
            self.statusBar().showMessage(message)
            QMessageBox.information(self, "Video Generated", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def save_settings(self):
        """Save current settings."""
        self.update_settings()
        if self.settings_manager.save_settings():
            QMessageBox.information(self, "Settings", "Settings saved successfully.")
        else:
            QMessageBox.warning(self, "Settings", "Failed to save settings.")
    
    def load_settings(self):
        """Load settings from file."""
        settings = self.settings_manager.load_settings()
        
        # Update UI with loaded settings
        mp3_path = settings.get('mp3_path', '')
        if mp3_path:
            self.mp3_path_input.setText(mp3_path)
            if os.path.exists(mp3_path):
                self.load_audio()
        
        bg_path = settings.get('background_path', '')
        if bg_path:
            self.bg_path_input.setText(bg_path)
        
        # Load video background path
        video_bg_path = settings.get('video_background_path', '')
        if video_bg_path and hasattr(self, 'bg_video_path_input'):
            self.bg_video_path_input.setText(video_bg_path)
        
        # Load background type
        bg_type = settings.get('background_type', 'image')
        if hasattr(self, 'bg_type_combo'):
            if bg_type == 'image':
                self.bg_type_combo.setCurrentText('Image')
            elif bg_type == 'video':
                self.bg_type_combo.setCurrentText('Video')
            elif bg_type == 'solid_color':
                self.bg_type_combo.setCurrentText('Solid Color')
        
        logo_path = settings.get('logo_path', '')
        if logo_path:
            self.logo_path_input.setText(logo_path)
        
        fit_setting = settings.get('background_fit', 'stretch')
        if fit_setting == 'stretch':
            self.bg_fit_combo.setCurrentText("Stretch to Fit")
        else:
            self.bg_fit_combo.setCurrentText(fit_setting.title())
        
        self.blur_slider.setValue(settings.get('background_blur', 0))
        self.blur_label.setText(str(settings.get('background_blur', 0)))
        self.bw_checkbox.setChecked(settings.get('background_bw', False))
        self.vignette_slider.setValue(settings.get('vignette_intensity', 0))
        self.vignette_label.setText(str(settings.get('vignette_intensity', 0)))
        
        self.strobe_checkbox.setChecked(settings.get('strobe_enabled', False))
        self.toggle_strobe_color(Qt.Checked if settings.get('strobe_enabled', False) else Qt.Unchecked)
        
        animation = settings.get('background_animation', 'none').replace('_', ' ').title()
        if animation == 'None':
            animation = 'None'
        elif animation == 'Fade In':
            animation = 'Fade In'
        self.animation_combo.setCurrentText(animation)
        
        self.auto_lyrics_checkbox.setChecked(settings.get('auto_lyrics', False))
        self.toggle_lyrics_input(Qt.Checked if settings.get('auto_lyrics', False) else Qt.Unchecked)
        self.lyrics_text.setPlainText(settings.get('lyrics_text', ''))
        self.text_overlay_input.setText(settings.get('text_overlay', ''))
        
        text_position = settings.get('text_position', 'center')
        self.text_position_combo.setCurrentText(text_position.title())
        
        # Visualizer settings
        if hasattr(self, 'visualizer_enabled_checkbox'):
            self.visualizer_enabled_checkbox.setChecked(settings.get('visualizer_enabled', True))
            self.toggle_visualizer_settings(Qt.Checked if settings.get('visualizer_enabled', True) else Qt.Unchecked)
        
        if hasattr(self, 'visualizer_style_combo'):
            style = settings.get('visualizer_style', 'filled_waveform').replace('_', ' ').title()
            # Match to combo box items
            style_map = {
                'Filled Waveform': 'Filled Waveform',
                'Bars': 'Bars',
                'Circle': 'Circle',
                'Line Waveform': 'Line Waveform',
                'Particle': 'Particle'
            }
            if style in style_map:
                self.visualizer_style_combo.setCurrentText(style_map[style])
        
        if hasattr(self, 'color_gradient_combo'):
            gradient = settings.get('color_gradient', 'pitch_rainbow').replace('_', ' ').title()
            gradient_map = {
                'Pitch Rainbow': 'Pitch Rainbow',
                'Frequency-Based': 'Frequency-based',
                'Energy-Based': 'Energy-based',
                'Custom': 'Custom',
                'Monochrome': 'Monochrome'
            }
            if gradient in gradient_map:
                self.color_gradient_combo.setCurrentText(gradient_map[gradient])
        
        if hasattr(self, 'orientation_combo'):
            orientation = settings.get('orientation', 'landscape_16_9')
            orientation_map = {
                'landscape_16_9': 'Landscape (16:9)',
                'portrait_9_16': 'Portrait (9:16)',
                'square_1_1': 'Square (1:1)',
                'ultrawide_21_9': 'Ultrawide (21:9)',
                'custom': 'Custom'
            }
            if orientation in orientation_map:
                self.orientation_combo.setCurrentText(orientation_map[orientation])
        
        if hasattr(self, 'resolution_combo'):
            resolution = settings.get('resolution', '1080p')
            resolution_map = {
                '1080p': '1080p (Full HD)',
                '720p': '720p (HD)',
                '2160p': '4K (2160p)',
                '1440p': '1440p (2K)',
                '480p': '480p (SD)',
                'custom': 'Custom'
            }
            if resolution in resolution_map:
                self.resolution_combo.setCurrentText(resolution_map[resolution])
            else:
                self.resolution_combo.setCurrentText('1080p (Full HD)')
        
        self.output_path_input.setText(settings.get('output_path', ''))
        
        self.update_settings()
        self.statusBar().showMessage("Settings loaded.")

