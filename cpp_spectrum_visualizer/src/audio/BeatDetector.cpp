/**
 * @file BeatDetector.cpp
 * @brief Implementation of beat detection
 */

#include "audio/BeatDetector.h"
#include <cmath>
#include <algorithm>
#include <numeric>
#include <iostream>

namespace Audio {

BeatDetector::BeatDetector(const std::vector<float>& audioData, int sampleRate)
    : audioData(audioData)
    , sampleRate(sampleRate)
    , hopLength(512)
{
}

bool BeatDetector::detectBeats(int hopLength) {
    if (audioData.empty()) {
        std::cerr << "No audio data for beat detection" << std::endl;
        return false;
    }
    
    this->hopLength = hopLength;
    
    // Compute onset strength function
    computeOnsetStrength(hopLength);
    
    // Find peaks in onset strength
    findPeaks(0.3f);
    
    // Estimate tempo
    beatInfo.tempo = estimateTempo();
    beatInfo.totalBeats = static_cast<int>(beatInfo.beatTimes.size());
    
    std::cout << "Detected " << beatInfo.totalBeats << " beats, tempo: " 
              << beatInfo.tempo << " BPM" << std::endl;
    
    return true;
}

void BeatDetector::computeOnsetStrength(int hopLength) {
    const int frameSize = 2048;
    int numFrames = (audioData.size() - frameSize) / hopLength + 1;
    
    onsetStrength.clear();
    onsetStrength.reserve(numFrames);
    
    std::vector<float> prevMagnitudes(frameSize / 2, 0.0f);
    
    for (int frame = 0; frame < numFrames; ++frame) {
        int startSample = frame * hopLength;
        
        // Simple energy-based onset detection
        float energy = 0.0f;
        for (int i = 0; i < frameSize && startSample + i < audioData.size(); ++i) {
            float sample = audioData[startSample + i];
            energy += sample * sample;
        }
        
        // High-frequency emphasis (simple high-pass)
        float hfEnergy = 0.0f;
        for (int i = frameSize / 2; i < frameSize && startSample + i < audioData.size(); ++i) {
            float sample = audioData[startSample + i];
            hfEnergy += sample * sample;
        }
        
        // Combine energy and high-frequency content
        float onset = std::sqrt(energy) + 2.0f * std::sqrt(hfEnergy);
        onsetStrength.push_back(onset);
    }
    
    // Normalize onset strength
    if (!onsetStrength.empty()) {
        float maxOnset = *std::max_element(onsetStrength.begin(), onsetStrength.end());
        if (maxOnset > 0.0f) {
            for (auto& val : onsetStrength) {
                val /= maxOnset;
            }
        }
    }
}

void BeatDetector::findPeaks(float threshold) {
    beatInfo.beatTimes.clear();
    
    if (onsetStrength.size() < 3) {
        return;
    }
    
    // Find local maxima above threshold
    for (size_t i = 1; i < onsetStrength.size() - 1; ++i) {
        if (onsetStrength[i] > threshold &&
            onsetStrength[i] > onsetStrength[i - 1] &&
            onsetStrength[i] > onsetStrength[i + 1]) {
            
            // Convert frame index to time
            double time = (i * hopLength) / static_cast<double>(sampleRate);
            beatInfo.beatTimes.push_back(time);
        }
    }
    
    // Remove beats that are too close together (minimum 0.2 seconds apart)
    if (beatInfo.beatTimes.size() > 1) {
        std::vector<double> filteredBeats;
        filteredBeats.push_back(beatInfo.beatTimes[0]);
        
        for (size_t i = 1; i < beatInfo.beatTimes.size(); ++i) {
            if (beatInfo.beatTimes[i] - filteredBeats.back() >= 0.2) {
                filteredBeats.push_back(beatInfo.beatTimes[i]);
            }
        }
        
        beatInfo.beatTimes = std::move(filteredBeats);
    }
}

double BeatDetector::estimateTempo() {
    if (beatInfo.beatTimes.size() < 2) {
        return 120.0; // Default tempo
    }
    
    // Calculate inter-beat intervals
    std::vector<double> intervals;
    for (size_t i = 1; i < beatInfo.beatTimes.size(); ++i) {
        intervals.push_back(beatInfo.beatTimes[i] - beatInfo.beatTimes[i - 1]);
    }
    
    // Use median interval to estimate tempo
    std::sort(intervals.begin(), intervals.end());
    double medianInterval = intervals[intervals.size() / 2];
    
    // Convert interval to BPM
    double bpm = 60.0 / medianInterval;
    
    // Clamp to reasonable range
    return std::clamp(bpm, 60.0, 200.0);
}

bool BeatDetector::isBeatFrame(int frameNumber, int frameRate, double tolerance) const {
    double frameTime = frameNumber / static_cast<double>(frameRate);
    
    for (double beatTime : beatInfo.beatTimes) {
        if (std::abs(frameTime - beatTime) <= tolerance) {
            return true;
        }
    }
    
    return false;
}

float BeatDetector::getBeatStrength(int frameNumber, int frameRate, float decayRate) const {
    double frameTime = frameNumber / static_cast<double>(frameRate);
    
    // Find most recent beat
    double lastBeatTime = -1.0;
    for (double beatTime : beatInfo.beatTimes) {
        if (beatTime <= frameTime) {
            lastBeatTime = beatTime;
        } else {
            break;
        }
    }
    
    if (lastBeatTime < 0.0) {
        return 0.0f;
    }
    
    // Calculate strength with exponential decay
    double timeSinceBeat = frameTime - lastBeatTime;
    float strength = std::exp(-timeSinceBeat * (1.0 - decayRate) * 10.0);
    
    return std::clamp(strength, 0.0f, 1.0f);
}

} // namespace Audio
