/**
 * @file BackgroundProcessor.cpp
 * @brief Implementation of background processor
 */

#include "effects/BackgroundProcessor.h"
#include <iostream>
#include <algorithm>
#include <cmath>

namespace Effects {

BackgroundProcessor::BackgroundProcessor(const std::string& videoPath, int targetFps)
    : videoPath(videoPath)
    , targetFps(targetFps)
    , videoFps(0.0)
    , totalFrames(0)
    , duration(0.0)
    , cacheLoaded(false)
{
}

BackgroundProcessor::~BackgroundProcessor() {
    close();
}

bool BackgroundProcessor::loadVideo() {
    if (!videoCapture.open(videoPath)) {
        std::cerr << "Error opening video: " << videoPath << std::endl;
        return false;
    }
    
    videoFps = videoCapture.get(cv::CAP_PROP_FPS);
    totalFrames = static_cast<int>(videoCapture.get(cv::CAP_PROP_FRAME_COUNT));
    duration = totalFrames / videoFps;
    
    if (duration <= 0) {
        std::cerr << "Invalid video duration" << std::endl;
        return false;
    }
    
    return true;
}

bool BackgroundProcessor::cacheFrames(int maxFrames) {
    if (!videoCapture.isOpened()) {
        if (!loadVideo()) {
            return false;
        }
    }
    
    frameCache.clear();
    videoCapture.set(cv::CAP_PROP_POS_FRAMES, 0);
    
    int framesToCache = (maxFrames > 0) ? std::min(maxFrames, totalFrames) : totalFrames;
    frameCache.reserve(framesToCache);
    
    for (int i = 0; i < framesToCache; ++i) {
        cv::Mat frame;
        if (!videoCapture.read(frame)) {
            break;
        }
        
        // Convert BGR to RGB
        cv::cvtColor(frame, frame, cv::COLOR_BGR2RGB);
        frameCache.push_back(frame.clone());
    }
    
    cacheLoaded = true;
    return true;
}

std::optional<cv::Mat> BackgroundProcessor::getFrameAtTime(double timeSeconds, const cv::Size& targetSize) {
    if (duration <= 0.0) {
        return std::nullopt;
    }
    
    // Loop video if time exceeds duration
    double loopedTime = std::fmod(timeSeconds, duration);
    
    // Calculate frame number
    int frameNumber = static_cast<int>(loopedTime * videoFps);
    frameNumber = std::clamp(frameNumber, 0, totalFrames - 1);
    
    cv::Mat frame;
    if (cacheLoaded && frameNumber < static_cast<int>(frameCache.size())) {
        frame = frameCache[frameNumber].clone();
    } else {
        auto optFrame = readFrameFromVideo(frameNumber);
        if (!optFrame) {
            return std::nullopt;
        }
        frame = *optFrame;
    }
    
    if (frame.empty()) {
        return std::nullopt;
    }
    
    // Resize to target size
    cv::Mat resized;
    cv::resize(frame, resized, targetSize, 0, 0, cv::INTER_LANCZOS4);
    
    return resized;
}

std::optional<cv::Mat> BackgroundProcessor::getFrameAtFrameNumber(int frameNumber, const cv::Size& targetSize) {
    double timeSeconds = frameNumber / static_cast<double>(targetFps);
    return getFrameAtTime(timeSeconds, targetSize);
}

std::optional<cv::Mat> BackgroundProcessor::readFrameFromVideo(int frameNumber) {
    if (!videoCapture.isOpened()) {
        if (!loadVideo()) {
            return std::nullopt;
        }
    }
    
    videoCapture.set(cv::CAP_PROP_POS_FRAMES, frameNumber);
    cv::Mat frame;
    
    if (videoCapture.read(frame)) {
        cv::cvtColor(frame, frame, cv::COLOR_BGR2RGB);
        return frame;
    }
    
    return std::nullopt;
}

void BackgroundProcessor::close() {
    if (videoCapture.isOpened()) {
        videoCapture.release();
    }
    frameCache.clear();
    cacheLoaded = false;
}

} // namespace Effects
