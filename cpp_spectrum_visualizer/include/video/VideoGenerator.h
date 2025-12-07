/**
 * @file VideoGenerator.h
 * @brief Main video generation orchestrator
 */

#pragma once

#include "audio/AudioProcessor.h"
#include "audio/BeatDetector.h"
#include "visualizers/BaseVisualizer.h"
#include "effects/BackgroundProcessor.h"
#include "effects/BeatEffects.h"
#include "video/FrameBuffer.h"
#include "video/VideoEncoder.h"
#include <memory>
#include <string>
#include <functional>

namespace Video {

/**
 * @struct GenerationSettings
 * @brief Settings for video generation
 */
struct GenerationSettings {
    // Video settings
    int width = 1920;
    int height = 1080;
    int fps = 30;
    
    // Visualizer settings
    std::string visualizerStyle = "bars";  // bars, waveform, circle, particle
    Visualizers::VisualizerSettings visualizerSettings;
    
    // Background settings
    std::string backgroundType = "solid";  // solid, image, video
    std::string backgroundPath = "";
    cv::Scalar solidColor = cv::Scalar(0, 0, 0);  // Black
    
    // Beat effects
    bool enableBeatEffects = true;
    std::string beatEffectType = "pulse";  // pulse, flash, strobe, zoom
    float beatEffectIntensity = 1.0f;
    
    // Encoding settings
    EncodingSettings encodingSettings;
    
    // Quality preset
    std::string qualityPreset = "balanced";  // fast, balanced, high
};

/**
 * @brief Progress callback type
 */
using ProgressCallback = std::function<void(int percent, const std::string& status)>;

/**
 * @class VideoGenerator
 * @brief Main class for generating video from audio
 */
class VideoGenerator {
public:
    VideoGenerator(Audio::AudioProcessor& audioProcessor, const GenerationSettings& settings);
    
    /**
     * @brief Generate video file
     * @param outputPath Output video file path
     * @param audioPath Audio file path (for encoding)
     * @param progressCallback Optional progress callback
     * @return True if successful
     */
    bool generateVideo(const std::string& outputPath, const std::string& audioPath,
                      ProgressCallback progressCallback = nullptr);
    
    /**
     * @brief Generate a single frame
     * @param frameNumber Frame number
     * @return Generated frame
     */
    cv::Mat generateFrame(int frameNumber);

private:
    void initializeVisualizer();
    void initializeBackground();
    cv::Mat createBackground(int frameNumber);
    cv::Mat applyEffects(const cv::Mat& frame, int frameNumber);
    
    Audio::AudioProcessor& audioProcessor;
    std::unique_ptr<Audio::BeatDetector> beatDetector;
    GenerationSettings settings;
    std::unique_ptr<Visualizers::BaseVisualizer> visualizer;
    std::unique_ptr<Effects::BackgroundProcessor> backgroundProcessor;
    std::unique_ptr<FrameBuffer> frameBuffer;
    std::unique_ptr<VideoEncoder> encoder;
    
    std::vector<float> currentBands;
    bool beatDetectionReady;
};

} // namespace Video
