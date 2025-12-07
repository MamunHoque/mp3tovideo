/**
 * @file BeatEffects.cpp
 * @brief Implementation of beat effects
 */

#include "effects/BeatEffects.h"
#include <algorithm>

namespace Effects {

cv::Mat applyBeatPulse(const cv::Mat& frame, float beatStrength, float scaleFactor) {
    if (beatStrength < 0.01f) {
        return frame.clone();
    }
    
    float scale = 1.0f + (scaleFactor - 1.0f) * beatStrength;
    
    int width = frame.cols;
    int height = frame.rows;
    int newWidth = static_cast<int>(width * scale);
    int newHeight = static_cast<int>(height * scale);
    
    cv::Mat scaled;
    cv::resize(frame, scaled, cv::Size(newWidth, newHeight), 0, 0, cv::INTER_LANCZOS4);
    
    // Crop back to original size (centered)
    int left = (newWidth - width) / 2;
    int top = (newHeight - height) / 2;
    
    cv::Rect roi(left, top, width, height);
    cv::Mat cropped = scaled(roi).clone();
    
    return cropped;
}

cv::Mat applyBeatFlash(const cv::Mat& frame, float beatStrength, 
                      const cv::Scalar& color, float maxIntensity) {
    if (beatStrength < 0.01f) {
        return frame.clone();
    }
    
    float intensity = beatStrength * maxIntensity;
    
    // Create flash overlay
    cv::Mat overlay(frame.size(), frame.type(), color);
    
    // Blend
    cv::Mat flashed;
    cv::addWeighted(frame, 1.0f - intensity, overlay, intensity, 0.0, flashed);
    
    return flashed;
}

cv::Mat applyBeatStrobe(const cv::Mat& frame, float beatStrength,
                       const cv::Scalar& color, float threshold) {
    if (beatStrength < threshold) {
        return frame.clone();
    }
    
    float intensity = std::min(0.8f, beatStrength);
    
    // Create strobe overlay
    cv::Mat overlay(frame.size(), frame.type(), color);
    
    // Blend
    cv::Mat strobed;
    cv::addWeighted(frame, 1.0f - intensity, overlay, intensity, 0.0, strobed);
    
    return strobed;
}

cv::Mat applyBeatZoom(const cv::Mat& frame, float beatStrength, float zoomAmount) {
    if (beatStrength < 0.01f) {
        return frame.clone();
    }
    
    float zoom = 1.0f + (zoomAmount * beatStrength);
    
    int width = frame.cols;
    int height = frame.rows;
    int newWidth = static_cast<int>(width / zoom);
    int newHeight = static_cast<int>(height / zoom);
    
    // Calculate crop box (centered)
    int left = (width - newWidth) / 2;
    int top = (height - newHeight) / 2;
    
    cv::Rect roi(left, top, newWidth, newHeight);
    cv::Mat cropped = frame(roi).clone();
    
    cv::Mat zoomed;
    cv::resize(cropped, zoomed, cv::Size(width, height), 0, 0, cv::INTER_LANCZOS4);
    
    return zoomed;
}

} // namespace Effects
