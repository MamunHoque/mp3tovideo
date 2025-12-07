/**
 * @file AudioProcessor.h
 * @brief Audio processing with FFTW3 for high-performance FFT analysis
 */

#pragma once

#include <vector>
#include <string>
#include <memory>
#include <optional>
#include <fftw3.h>

namespace Audio {

/**
 * @class AudioProcessor
 * @brief Processes audio files and extracts spectrum data for visualization
 */
class AudioProcessor {
public:
    /**
     * @brief Constructor
     * @param audioPath Path to audio file (MP3, WAV, etc.)
     */
    explicit AudioProcessor(const std::string& audioPath);
    
    /**
     * @brief Destructor - cleans up FFTW resources
     */
    ~AudioProcessor();
    
    // Disable copy, enable move
    AudioProcessor(const AudioProcessor&) = delete;
    AudioProcessor& operator=(const AudioProcessor&) = delete;
    AudioProcessor(AudioProcessor&&) noexcept;
    AudioProcessor& operator=(AudioProcessor&&) noexcept;
    
    /**
     * @brief Load audio file
     * @return True if successful
     */
    bool loadAudio();
    
    /**
     * @brief Get audio duration in seconds
     * @return Duration in seconds
     */
    double getDuration() const { return duration; }
    
    /**
     * @brief Get sample rate
     * @return Sample rate in Hz
     */
    int getSampleRate() const { return sampleRate; }
    
    /**
     * @brief Compute spectrum for all frames
     * @param frameRate Video frame rate (fps)
     * @param nFft Number of FFT points (default 2048)
     * @return True if successful
     */
    bool computeSpectrum(int frameRate = 30, int nFft = 2048);
    
    /**
     * @brief Get frequency bands for visualization
     * @param numBands Number of frequency bands (default 64)
     * @param frameRate Video frame rate
     * @return True if successful
     */
    bool getFrequencyBands(int numBands = 64, int frameRate = 30);
    
    /**
     * @brief Get spectrum data for a specific frame
     * @param frameNumber Frame number (0-indexed)
     * @return Spectrum magnitudes (empty if invalid frame)
     */
    std::vector<float> getFrameSpectrum(int frameNumber) const;
    
    /**
     * @brief Get frequency bands for a specific frame
     * @param frameNumber Frame number (0-indexed)
     * @return Band magnitudes (empty if invalid frame)
     */
    std::vector<float> getFrameBands(int frameNumber) const;
    
    /**
     * @brief Get audio intensity for a frame (for strobe effects)
     * @param frameNumber Frame number
     * @param frameRate Video frame rate
     * @param windowSize Number of frames to average over
     * @return Intensity value (0.0 to 1.0)
     */
    float getAudioIntensity(int frameNumber, int frameRate = 30, int windowSize = 10) const;
    
    /**
     * @brief Check if audio is loaded
     * @return True if audio data is available
     */
    bool isLoaded() const { return !audioData.empty(); }
    
    /**
     * @brief Get total number of frames
     * @return Number of frames for current frame rate
     */
    int getTotalFrames() const { return static_cast<int>(spectrumCache.size()); }

private:
    void cleanup();
    void resampleSpectrum(int targetFrames);
    
    std::string audioPath;
    std::vector<float> audioData;
    int sampleRate;
    double duration;
    
    // FFT data
    int nFft;
    int frameRate;
    fftw_plan fftwPlan;
    double* fftwIn;
    fftw_complex* fftwOut;
    
    // Cached spectrum data
    std::vector<std::vector<float>> spectrumCache;  // [frame][frequency_bin]
    std::vector<std::vector<float>> bandsCache;     // [frame][band]
    int numBands;
};

} // namespace Audio
