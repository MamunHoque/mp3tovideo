/**
 * @file BeatDetector.h
 * @brief Beat detection for audio-reactive effects
 */

#pragma once

#include <vector>
#include <string>

namespace Audio {

/**
 * @struct BeatInfo
 * @brief Information about detected beats
 */
struct BeatInfo {
    std::vector<double> beatTimes;  // Beat timestamps in seconds
    double tempo;                    // BPM (beats per minute)
    int totalBeats;                  // Total number of beats detected
};

/**
 * @class BeatDetector
 * @brief Detects beats in audio for synchronization effects
 */
class BeatDetector {
public:
    /**
     * @brief Constructor
     * @param audioData Audio samples (mono)
     * @param sampleRate Sample rate in Hz
     */
    BeatDetector(const std::vector<float>& audioData, int sampleRate);
    
    /**
     * @brief Detect beats in the audio
     * @param hopLength Number of samples between analysis frames
     * @return True if successful
     */
    bool detectBeats(int hopLength = 512);
    
    /**
     * @brief Get beat information
     * @return BeatInfo structure with detected beats
     */
    const BeatInfo& getBeatInfo() const { return beatInfo; }
    
    /**
     * @brief Check if a frame is on a beat
     * @param frameNumber Frame number
     * @param frameRate Video frame rate
     * @param tolerance Tolerance window in seconds
     * @return True if frame is on or near a beat
     */
    bool isBeatFrame(int frameNumber, int frameRate, double tolerance = 0.05) const;
    
    /**
     * @brief Get beat strength for a frame (with decay)
     * @param frameNumber Frame number
     * @param frameRate Video frame rate
     * @param decayRate Decay rate (0.0 to 1.0)
     * @return Beat strength (0.0 to 1.0)
     */
    float getBeatStrength(int frameNumber, int frameRate, float decayRate = 0.9f) const;
    
    /**
     * @brief Get tempo in BPM
     * @return Tempo
     */
    double getTempo() const { return beatInfo.tempo; }
    
    /**
     * @brief Get all beat times
     * @return Vector of beat timestamps
     */
    const std::vector<double>& getBeatTimes() const { return beatInfo.beatTimes; }

private:
    void computeOnsetStrength(int hopLength);
    void findPeaks(float threshold);
    double estimateTempo();
    
    const std::vector<float>& audioData;
    int sampleRate;
    BeatInfo beatInfo;
    std::vector<float> onsetStrength;
    int hopLength;
};

} // namespace Audio


