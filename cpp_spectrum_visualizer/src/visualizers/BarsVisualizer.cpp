/**
 * @file BarsVisualizer.cpp
 * @brief Implementation of bars visualizer
 */

#include "visualizers/BarsVisualizer.h"

namespace Visualizers {

BarsVisualizer::BarsVisualizer(const VisualizerSettings& settings)
    : BaseVisualizer(settings)
    , barWidth(20)
    , barSpacing(5)
{
}

cv::Mat BarsVisualizer::render(const std::vector<float>& bands, const cv::Mat& background) {
    cv::Mat frame = background.clone();
    
    if (bands.empty()) {
        return frame;
    }
    
    smoothBands(bands);
    
    int numBands = smoothedBands.size();
    int totalWidth = numBands * (barWidth + barSpacing);
    int startX = (settings.width - totalWidth) / 2;
    int baseY = settings.height - 100;
    int maxHeight = settings.height / 2;
    
    for (int i = 0; i < numBands; ++i) {
        float magnitude = smoothedBands[i] * settings.scale;
        magnitude = std::min(magnitude, 1.0f);
        
        int barHeight = static_cast<int>(magnitude * maxHeight);
        int x = startX + i * (barWidth + barSpacing);
        int y = baseY - barHeight;
        
        cv::Scalar color = getColor(i, numBands, magnitude);
        
        // Draw bar
        cv::rectangle(frame, 
                     cv::Point(x, y), 
                     cv::Point(x + barWidth, baseY),
                     color, 
                     cv::FILLED);
        
        // Draw outline
        cv::rectangle(frame, 
                     cv::Point(x, y), 
                     cv::Point(x + barWidth, baseY),
                     cv::Scalar(255, 255, 255), 
                     1);
    }
    
    return frame;
}

} // namespace Visualizers
