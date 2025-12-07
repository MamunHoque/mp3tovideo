/**
 * @file CircleVisualizer.cpp
 * @brief Implementation of circle visualizer
 */

#include "visualizers/CircleVisualizer.h"
#include <algorithm>
#include <cmath>

namespace Visualizers {

CircleVisualizer::CircleVisualizer(const VisualizerSettings& settings)
    : BaseVisualizer(settings)
{
}

cv::Mat CircleVisualizer::render(const std::vector<float>& bands, const cv::Mat& background) {
    cv::Mat frame;
    background.copyTo(frame);
    
    if (bands.empty()) {
        return frame;
    }
    
    smoothBands(bands);
    const auto& bandsToRender = smoothedBands.empty() ? bands : smoothedBands;
    
    int numBands = static_cast<int>(bandsToRender.size());
    int centerX = settings.width / 2;
    int centerY = settings.height / 2;
    int baseRadius = std::min(settings.width, settings.height) / 4;
    float angleStep = 2.0f * M_PI / numBands;
    
    // Draw bars radiating from center
    for (int i = 0; i < numBands; ++i) {
        float magnitude = std::clamp(bandsToRender[i] * settings.scale, 0.0f, 1.0f);
        float angle = i * angleStep;
        int barLength = static_cast<int>(magnitude * baseRadius * 1.5);
        
        int startX = centerX + static_cast<int>(baseRadius * std::cos(angle));
        int startY = centerY + static_cast<int>(baseRadius * std::sin(angle));
        int endX = startX + static_cast<int>(barLength * std::cos(angle));
        int endY = startY + static_cast<int>(barLength * std::sin(angle));
        
        cv::Scalar color = getColor(i, numBands, magnitude);
        
        // Draw bar
        cv::line(frame,
                cv::Point(startX, startY),
                cv::Point(endX, endY),
                color,
                3);
        
        // Draw circle at end of bar
        cv::circle(frame,
                  cv::Point(endX, endY),
                  5,
                  color,
                  -1);
    }
    
    // Draw center circle
    cv::circle(frame,
              cv::Point(centerX, centerY),
              baseRadius,
              cv::Scalar(100, 100, 100),
              2);
    
    return frame;
}

} // namespace Visualizers
