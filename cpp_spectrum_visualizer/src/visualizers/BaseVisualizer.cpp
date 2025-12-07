/**
 * @file BaseVisualizer.cpp
 * @brief Implementation of base visualizer
 */

#include "visualizers/BaseVisualizer.h"
#include <algorithm>

namespace Visualizers {

BaseVisualizer::BaseVisualizer(const VisualizerSettings& settings)
    : settings(settings)
{
    // Initialize color gradient based on type
    if (settings.gradientType == ColorGradientType::Custom && !settings.customColors.empty()) {
        std::vector<cv::Vec3b> colors;
        for (const auto& color : settings.customColors) {
            colors.push_back(cv::Vec3b(color[0], color[1], color[2]));
        }
        colorGradient = Utils::ColorGradient(colors);
    } else {
        // Default rainbow gradient
        colorGradient = Utils::ColorGradient({
            cv::Vec3b(255, 0, 0),    // Blue
            cv::Vec3b(0, 255, 0),    // Green
            cv::Vec3b(0, 255, 255),  // Yellow
            cv::Vec3b(0, 0, 255)     // Red
        });
    }
}

cv::Scalar BaseVisualizer::getColor(int bandIndex, int numBands, float magnitude) {
    cv::Vec3b color;
    
    switch (settings.gradientType) {
        case ColorGradientType::PitchRainbow: {
            float t = static_cast<float>(bandIndex) / numBands;
            color = colorGradient.getColor(t);
            break;
        }
        
        case ColorGradientType::FrequencyBased: {
            float t = static_cast<float>(bandIndex) / numBands;
            if (t < 0.33f) {
                // Low frequencies: Red
                color = cv::Vec3b(0, 0, 255);
            } else if (t < 0.67f) {
                // Mid frequencies: Green
                color = cv::Vec3b(0, 255, 0);
            } else {
                // High frequencies: Blue
                color = cv::Vec3b(255, 0, 0);
            }
            break;
        }
        
        case ColorGradientType::EnergyBased: {
            color = colorGradient.getColor(magnitude);
            break;
        }
        
        case ColorGradientType::Custom: {
            float t = static_cast<float>(bandIndex) / numBands;
            color = colorGradient.getColor(t);
            break;
        }
        
        case ColorGradientType::Monochrome: {
            // Scale monochrome color by magnitude
            color = cv::Vec3b(
                settings.monochromeColor[0] * magnitude,
                settings.monochromeColor[1] * magnitude,
                settings.monochromeColor[2] * magnitude
            );
            break;
        }
    }
    
    return cv::Scalar(color[0], color[1], color[2]);
}

void BaseVisualizer::updateSettings(const VisualizerSettings& newSettings) {
    settings = newSettings;
    
    // Update color gradient if needed
    if (settings.gradientType == ColorGradientType::Custom && !settings.customColors.empty()) {
        std::vector<cv::Vec3b> colors;
        for (const auto& color : settings.customColors) {
            colors.push_back(cv::Vec3b(color[0], color[1], color[2]));
        }
        colorGradient = Utils::ColorGradient(colors);
    }
}

void BaseVisualizer::smoothBands(const std::vector<float>& bands) {
    if (smoothedBands.empty()) {
        smoothedBands = bands;
        return;
    }
    
    if (smoothedBands.size() != bands.size()) {
        smoothedBands.resize(bands.size());
    }
    
    for (size_t i = 0; i < bands.size(); ++i) {
        smoothedBands[i] = smoothedBands[i] * settings.smoothing + 
                          bands[i] * (1.0f - settings.smoothing);
    }
}

} // namespace Visualizers
