"""
Audio processing module for MP3 Spectrum Visualizer.
Handles audio loading, spectrum analysis, and timing information.
"""

import librosa
import numpy as np
from typing import Tuple, List, Optional


class AudioProcessor:
    """Processes audio files and extracts spectrum data for visualization."""
    
    def __init__(self, audio_path: str):
        """
        Initialize audio processor with an audio file.
        
        Args:
            audio_path: Path to the MP3 audio file
        """
        self.audio_path = audio_path
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: Optional[int] = None
        self.duration: Optional[float] = None
        self._spectrum_cache: Optional[np.ndarray] = None
        self._beat_frames: Optional[np.ndarray] = None
        self._beat_times: Optional[np.ndarray] = None
        self._tempo: Optional[float] = None
        self._onset_envelope: Optional[np.ndarray] = None
        
    def load_audio(self) -> Tuple[np.ndarray, int]:
        """
        Load audio file and extract data.
        
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        if self.audio_data is None:
            self.audio_data, self.sample_rate = librosa.load(
                self.audio_path,
                sr=None,  # Keep original sample rate
                mono=True  # Convert to mono
            )
            self.duration = librosa.get_duration(
                y=self.audio_data,
                sr=self.sample_rate
            )
        return self.audio_data, self.sample_rate
    
    def get_duration(self) -> float:
        """Get the duration of the audio in seconds."""
        if self.duration is None:
            self.load_audio()
        return self.duration
    
    def compute_spectrum(self, frame_rate: int = 30, n_fft: int = 2048) -> np.ndarray:
        """
        Compute spectrum data for each video frame.
        
        Args:
            frame_rate: Video frame rate (fps)
            n_fft: Number of FFT points
            
        Returns:
            Array of shape (num_frames, n_fft//2 + 1) containing spectrum magnitudes
        """
        if self._spectrum_cache is not None:
            return self._spectrum_cache
        
        audio_data, sr = self.load_audio()
        duration = self.get_duration()
        num_frames = int(duration * frame_rate)
        
        # Calculate hop length for frame-by-frame analysis
        hop_length = len(audio_data) // num_frames if num_frames > 0 else 512
        
        # Compute short-time Fourier transform
        stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        # Resample to match exact number of frames
        if magnitude.shape[1] != num_frames:
            # Use numpy interpolation to match frame count
            original_indices = np.linspace(0, magnitude.shape[1] - 1, magnitude.shape[1])
            target_indices = np.linspace(0, magnitude.shape[1] - 1, num_frames)
            # Interpolate each frequency bin
            resampled = np.zeros((magnitude.shape[0], num_frames))
            for i in range(magnitude.shape[0]):
                resampled[i] = np.interp(target_indices, original_indices, magnitude[i])
            magnitude = resampled
        
        self._spectrum_cache = magnitude
        return magnitude
    
    def get_frequency_bands(self, num_bands: int = 64, frame_rate: int = 30) -> np.ndarray:
        """
        Get frequency bands for visualization.
        
        Args:
            num_bands: Number of frequency bands to create
            frame_rate: Video frame rate
            
        Returns:
            Array of shape (num_frames, num_bands) with band magnitudes
        """
        spectrum = self.compute_spectrum(frame_rate=frame_rate)
        n_fft = spectrum.shape[0]
        
        # Map FFT bins to frequency bands
        bands = np.zeros((spectrum.shape[1], num_bands))
        
        for i in range(num_bands):
            # Use logarithmic spacing for frequency bands
            start_bin = int((i / num_bands) ** 2 * n_fft)
            end_bin = int(((i + 1) / num_bands) ** 2 * n_fft)
            end_bin = min(end_bin, n_fft)
            
            if start_bin < end_bin:
                bands[:, i] = np.mean(spectrum[start_bin:end_bin, :].T, axis=1)
        
        return bands
    
    def get_frame_spectrum(self, frame_number: int, frame_rate: int = 30) -> np.ndarray:
        """
        Get spectrum data for a specific frame.
        
        Args:
            frame_number: Frame number (0-indexed)
            frame_rate: Video frame rate
            
        Returns:
            Array of spectrum magnitudes for the frame
        """
        spectrum = self.compute_spectrum(frame_rate=frame_rate)
        if frame_number >= spectrum.shape[1]:
            frame_number = spectrum.shape[1] - 1
        return spectrum[:, frame_number]
    
    def get_frame_bands(self, frame_number: int, num_bands: int = 64, frame_rate: int = 30) -> np.ndarray:
        """
        Get frequency bands for a specific frame.
        
        Args:
            frame_number: Frame number (0-indexed)
            num_bands: Number of frequency bands
            frame_rate: Video frame rate
            
        Returns:
            Array of band magnitudes for the frame
        """
        bands = self.get_frequency_bands(num_bands=num_bands, frame_rate=frame_rate)
        if frame_number >= bands.shape[0]:
            frame_number = bands.shape[0] - 1
        return bands[frame_number]
    
    def get_audio_intensity(self, frame_number: int, frame_rate: int = 30, window_size: int = 10) -> float:
        """
        Get audio intensity for a frame (useful for strobe effects).
        
        Args:
            frame_number: Frame number (0-indexed)
            frame_rate: Video frame rate
            window_size: Number of frames to average over
            
        Returns:
            Intensity value (0.0 to 1.0)
        """
        bands = self.get_frequency_bands(num_bands=64, frame_rate=frame_rate)
        start_frame = max(0, frame_number - window_size // 2)
        end_frame = min(bands.shape[0], frame_number + window_size // 2)
        
        if start_frame >= end_frame:
            return 0.0
        
        # Calculate RMS energy
        energy = np.mean(bands[start_frame:end_frame])
        # Normalize (this is a simple normalization, may need tuning)
        intensity = min(1.0, energy / 0.1)  # Adjust threshold as needed
        return float(intensity)
    
    def detect_beats(self) -> Tuple[float, np.ndarray]:
        """
        Detect beats in the audio.
        
        Returns:
            Tuple of (tempo in BPM, beat frame numbers)
        """
        if self._tempo is not None and self._beat_frames is not None:
            return self._tempo, self._beat_frames
        
        audio_data, sr = self.load_audio()
        
        # Detect tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sr)
        
        # Convert tempo from array to float if needed
        if isinstance(tempo, np.ndarray):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            tempo = float(tempo)
        
        # Convert beat frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        self._tempo = tempo
        self._beat_frames = beat_frames
        self._beat_times = beat_times
        
        return tempo, beat_frames
    
    def get_tempo(self) -> float:
        """
        Get the tempo (BPM) of the audio.
        
        Returns:
            Tempo in beats per minute
        """
        if self._tempo is None:
            self.detect_beats()
        return self._tempo if self._tempo else 120.0
    
    def get_beat_times(self) -> np.ndarray:
        """
        Get beat timestamps in seconds.
        
        Returns:
            Array of beat times in seconds
        """
        if self._beat_times is None:
            self.detect_beats()
        return self._beat_times if self._beat_times is not None else np.array([])
    
    def is_beat_frame(self, frame_number: int, frame_rate: int = 30, tolerance: int = 2) -> bool:
        """
        Check if a frame is close to a beat.
        
        Args:
            frame_number: Frame number to check
            frame_rate: Video frame rate
            tolerance: Number of frames tolerance around beat
            
        Returns:
            True if frame is near a beat
        """
        beat_times = self.get_beat_times()
        if len(beat_times) == 0:
            return False
        
        # Convert frame number to time
        frame_time = frame_number / frame_rate
        
        # Check if any beat is within tolerance
        for beat_time in beat_times:
            time_diff = abs(frame_time - beat_time)
            frame_diff = time_diff * frame_rate
            if frame_diff <= tolerance:
                return True
        
        return False
    
    def get_beat_strength(self, frame_number: int, frame_rate: int = 30) -> float:
        """
        Get beat strength for a frame (0.0 to 1.0).
        
        Args:
            frame_number: Frame number
            frame_rate: Video frame rate
            
        Returns:
            Beat strength (1.0 at beat, fades to 0.0)
        """
        beat_times = self.get_beat_times()
        if len(beat_times) == 0:
            return 0.0
        
        frame_time = frame_number / frame_rate
        
        # Find closest beat
        time_diffs = np.abs(beat_times - frame_time)
        min_diff = np.min(time_diffs)
        
        # Convert to frame difference
        frame_diff = min_diff * frame_rate
        
        # Calculate strength (exponential decay)
        if frame_diff < 10:  # Within 10 frames
            strength = np.exp(-frame_diff / 3.0)  # Decay factor
            return float(np.clip(strength, 0.0, 1.0))
        
        return 0.0
    
    def compute_onset_envelope(self) -> np.ndarray:
        """
        Compute onset strength envelope for rhythm analysis.
        
        Returns:
            Onset strength envelope
        """
        if self._onset_envelope is not None:
            return self._onset_envelope
        
        audio_data, sr = self.load_audio()
        
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        
        self._onset_envelope = onset_env
        return onset_env

