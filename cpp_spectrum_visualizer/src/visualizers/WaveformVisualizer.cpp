/**
 * @file WaveformVisualizer.cpp
 * @brief Implementation of waveform visualizer
 */

#include "visualizers/WaveformVisualizer.h"
#include <algorithm>
#include <cmath>

namespace Visualizers {

WaveformVisualizer::WaveformVisualizer(const VisualizerSettings& settings)
    : BaseVisualizer(settings)
{
}

cv::Mat WaveformVisualizer::render(const std::vector<float>& bands, const cv::Mat& background) {
    cv::Mat frame;
    background.copyTo(frame);
    
    if (bands.empty()) {
        return frame;
    }
    
    smoothBands(bands);
    const auto& bandsToRender = smoothedBands.empty() ? bands : smoothedBands;
    
    int numBands = static_cast<int>(bandsToRender.size());
    int centerY = settings.height / 2;
    float xStep = static_cast<float>(settings.width) / numBands;
    
    // Create polygon points for filled waveform
    std::vector<cv::Point> points;
    points.reserve(numBands * 2);
    
    // Top half of waveform
    for (int i = 0; i < numBands; ++i) {
        float magnitude = std::clamp(bandsToRender[i] * settings.scale, 0.0f, 1.0f);
        int y = centerY - static_cast<int>(magnitude * settings.height * 0.4);
        points.push_back(cv::Point(static_cast<int>(i * xStep), y));
    }
    
    // Bottom half of waveform (mirror)
    for (int i = numBands - 1; i >= 0; --i) {
        float magnitude = std::clamp(bandsToRender[i] * settings.scale, 0.0f, 1.0f);
        int y = centerY + static_cast<int>(magnitude * settings.height * 0.4);
        points.push_back(cv::Point(static_cast<int>(i * xStep), y));
    }
    
    if (points.size() >= 3) {
        // Draw filled polygon
        std::vector<std::vector<cv::Point>> contours = {points};
        cv::fillPoly(frame, contours, cv::Scalar(255, 255, 255));
        
        // Draw gradient overlay
        for (size_t i = 0; i < bandsToRender.size() && i < static_cast<size_t>(points.size() / 2); ++i) {
            if (i < points.size() / 2) {
                cv::Scalar color = getColor(static_cast<int>(i), numBands, bandsToRender[i]);
                
                // Draw line segment with gradient color
                if (i > 0) {
                    cv::line(frame, points[i - 1], points[i], color, 3);
                }
            }
        }
    }
    
    return frame;
}

} // namespace Visualizers
