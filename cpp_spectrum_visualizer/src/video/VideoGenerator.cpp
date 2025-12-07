/**
 * @file VideoGenerator.cpp
 * @brief Implementation of video generator
 */

#include "video/VideoGenerator.h"
#include "visualizers/BarsVisualizer.h"
#include "visualizers/WaveformVisualizer.h"
#include "visualizers/CircleVisualizer.h"
#include "visualizers/ParticleVisualizer.h"
#include <iostream>
#include <filesystem>
#include <cmath>
#include <memory>

namespace Video {

VideoGenerator::VideoGenerator(Audio::AudioProcessor& audioProcessor, const GenerationSettings& settings)
    : audioProcessor(audioProcessor)
    , settings(settings)
    , beatDetectionReady(false)
{
    // Update encoding settings with video dimensions
    this->settings.encodingSettings.width = settings.width;
    this->settings.encodingSettings.height = settings.height;
    this->settings.encodingSettings.fps = settings.fps;
    
    // Initialize beat detector (will be done after audio is loaded)
    beatDetectionReady = false;
    
    // Initialize visualizer
    initializeVisualizer();
    
    // Initialize background
    initializeBackground();
    
    // Initialize frame buffer
    std::filesystem::path tempDir = std::filesystem::temp_directory_path() / "spectrum_viz";
    frameBuffer = std::make_unique<FrameBuffer>(tempDir.string());
    
    // Initialize encoder
    encoder = std::make_unique<VideoEncoder>(settings.encodingSettings);
}

void VideoGenerator::initializeVisualizer() {
    settings.visualizerSettings.width = settings.width;
    settings.visualizerSettings.height = settings.height;
    
    if (settings.visualizerStyle == "bars") {
        visualizer = std::make_unique<Visualizers::BarsVisualizer>(settings.visualizerSettings);
    }
    else if (settings.visualizerStyle == "waveform") {
        visualizer = std::make_unique<Visualizers::WaveformVisualizer>(settings.visualizerSettings);
    }
    else if (settings.visualizerStyle == "circle") {
        visualizer = std::make_unique<Visualizers::CircleVisualizer>(settings.visualizerSettings);
    }
    else if (settings.visualizerStyle == "particle") {
        visualizer = std::make_unique<Visualizers::ParticleVisualizer>(settings.visualizerSettings);
    }
    else {
        // Default to bars
        visualizer = std::make_unique<Visualizers::BarsVisualizer>(settings.visualizerSettings);
    }
}

void VideoGenerator::initializeBackground() {
    if (settings.backgroundType == "video" && !settings.backgroundPath.empty()) {
        if (std::filesystem::exists(settings.backgroundPath)) {
            backgroundProcessor = std::make_unique<Effects::BackgroundProcessor>(
                settings.backgroundPath, settings.fps
            );
            if (!backgroundProcessor->loadVideo()) {
                backgroundProcessor.reset();
            } else {
                // Cache frames if video is short
                if (backgroundProcessor->getDuration() < 30.0) {
                    backgroundProcessor->cacheFrames();
                }
            }
        }
    }
}

cv::Mat VideoGenerator::createBackground(int frameNumber) {
    if (settings.backgroundType == "solid") {
        cv::Mat bg(settings.height, settings.width, CV_8UC3, settings.solidColor);
        return bg;
    }
    else if (settings.backgroundType == "image" && !settings.backgroundPath.empty()) {
        if (std::filesystem::exists(settings.backgroundPath)) {
            cv::Mat img = cv::imread(settings.backgroundPath, cv::IMREAD_COLOR);
            if (!img.empty()) {
                cv::Mat resized;
                cv::resize(img, resized, cv::Size(settings.width, settings.height), 0, 0, cv::INTER_LANCZOS4);
                cv::cvtColor(resized, resized, cv::COLOR_BGR2RGB);
                return resized;
            }
        }
    }
    else if (settings.backgroundType == "video" && backgroundProcessor) {
        double timeSeconds = frameNumber / static_cast<double>(settings.fps);
        auto frame = backgroundProcessor->getFrameAtTime(timeSeconds, cv::Size(settings.width, settings.height));
        if (frame) {
            return *frame;
        }
    }
    
    // Default to solid color
    cv::Mat bg(settings.height, settings.width, CV_8UC3, settings.solidColor);
    return bg;
}

cv::Mat VideoGenerator::applyEffects(const cv::Mat& frame, int frameNumber) {
    cv::Mat result = frame.clone();
    
    if (!settings.enableBeatEffects || !beatDetectionReady) {
        return result;
    }
    
    float beatStrength = beatDetector->getBeatStrength(frameNumber, settings.fps);
    
    if (beatStrength > 0.01f) {
        if (settings.beatEffectType == "pulse") {
            result = Effects::applyBeatPulse(result, beatStrength, 1.0f + settings.beatEffectIntensity * 0.1f);
        }
        else if (settings.beatEffectType == "flash") {
            result = Effects::applyBeatFlash(result, beatStrength, cv::Scalar(255, 255, 255), 
                                           settings.beatEffectIntensity * 0.3f);
        }
        else if (settings.beatEffectType == "strobe") {
            result = Effects::applyBeatStrobe(result, beatStrength, cv::Scalar(255, 255, 255), 0.5f);
        }
        else if (settings.beatEffectType == "zoom") {
            result = Effects::applyBeatZoom(result, beatStrength, settings.beatEffectIntensity * 0.05f);
        }
    }
    
    return result;
}

cv::Mat VideoGenerator::generateFrame(int frameNumber) {
    // Get frequency bands for this frame
    currentBands = audioProcessor.getFrameBands(frameNumber);
    
    // Create background
    cv::Mat background = createBackground(frameNumber);
    
    // Render visualizer
    cv::Mat frame = visualizer->render(currentBands, background);
    
    // Apply effects
    frame = applyEffects(frame, frameNumber);
    
    return frame;
}

bool VideoGenerator::generateVideo(const std::string& outputPath, const std::string& audioPath,
                                  ProgressCallback progressCallback) {
    if (!audioProcessor.isLoaded()) {
        std::cerr << "Audio not loaded" << std::endl;
        return false;
    }
    
    // Initialize beat detector if needed
    if (settings.enableBeatEffects && !beatDetectionReady) {
        beatDetector = std::make_unique<Audio::BeatDetector>(
            audioProcessor.getAudioData(), audioProcessor.getSampleRate()
        );
        beatDetector->detectBeats();
        beatDetectionReady = true;
    }
    
    // Compute spectrum if not already done
    if (audioProcessor.getTotalFrames() == 0) {
        if (progressCallback) progressCallback(0, "Computing spectrum...");
        if (!audioProcessor.computeSpectrum(settings.fps)) {
            std::cerr << "Failed to compute spectrum" << std::endl;
            return false;
        }
        if (!audioProcessor.getFrequencyBands(64, settings.fps)) {
            std::cerr << "Failed to compute frequency bands" << std::endl;
            return false;
        }
    }
    
    int totalFrames = audioProcessor.getTotalFrames();
    
    // Generate frames
    if (progressCallback) progressCallback(5, "Generating frames...");
    
    for (int frame = 0; frame < totalFrames; ++frame) {
        cv::Mat frameImage = generateFrame(frame);
        frameBuffer->saveFrame(frameImage, frame);
        
        if (progressCallback && frame % 10 == 0) {
            int percent = 5 + (frame * 85 / totalFrames);
            progressCallback(percent, "Generating frames...");
        }
    }
    
    // Encode video
    if (progressCallback) progressCallback(90, "Encoding video...");
    
    bool success = encoder->encode(frameBuffer->getTempDir(), outputPath, audioPath);
    
    if (progressCallback) {
        progressCallback(success ? 100 : 0, success ? "Complete" : "Failed");
    }
    
    return success;
}

} // namespace Video
