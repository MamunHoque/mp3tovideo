/**
 * @file BarsVisualizer.cpp
 * @brief Implementation of bars visualizer
 */

#include "visualizers/BarsVisualizer.h"
#include <algorithm>

namespace Visualizers {

BarsVisualizer::BarsVisualizer(const VisualizerSettings& settings)
    : BaseVisualizer(settings)
{
}

cv::Mat BarsVisualizer::render(const std::vector<float>& bands, const cv::Mat& background) {
    cv::Mat frame;
    background.copyTo(frame);
    
    if (bands.empty()) {
        return frame;
    }
    
    smoothBands(bands);
    const auto& bandsToRender = smoothedBands.empty() ? bands : smoothedBands;
    
    int numBands = static_cast<int>(bandsToRender.size());
    int barWidth = settings.width / (numBands + 1);
    int maxBarHeight = settings.height * 0.8;
    int centerY = settings.height / 2;
    
    for (int i = 0; i < numBands; ++i) {
        float magnitude = std::clamp(bandsToRender[i] * settings.scale, 0.0f, 1.0f);
        int barHeight = static_cast<int>(magnitude * maxBarHeight);
        
        int x = (i + 1) * barWidth;
        int topY = centerY - barHeight / 2;
        int bottomY = centerY + barHeight / 2;
        
        cv::Scalar color = getColor(i, numBands, magnitude);
        
        // Draw bar
        cv::rectangle(frame,
                     cv::Point(x - barWidth / 2, topY),
                     cv::Point(x + barWidth / 2, bottomY),
                     color,
                     -1);
        
        // Add glow effect
        cv::Scalar glowColor = color * 0.3;
        cv::rectangle(frame,
                     cv::Point(x - barWidth / 2 - 2, topY - 2),
                     cv::Point(x + barWidth / 2 + 2, bottomY + 2),
                     glowColor,
                     1);
    }
    
    return frame;
}

} // namespace Visualizers
