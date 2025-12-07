/**
 * @file WaveformVisualizer.cpp
 * @brief Implementation of waveform visualizer
 */

#include "visualizers/WaveformVisualizer.h"

namespace Visualizers {

WaveformVisualizer::WaveformVisualizer(const VisualizerSettings& settings)
    : BaseVisualizer(settings)
{
}

cv::Mat WaveformVisualizer::render(const std::vector<float>& bands, const cv::Mat& background) {
    cv::Mat frame = background.clone();
    
    if (bands.empty()) {
        return frame;
    }
    
    smoothBands(bands);
    
    int numBands = smoothedBands.size();
    int centerY = settings.height / 2;
    int maxAmplitude = settings.height / 3;
    
    std::vector<cv::Point> topPoints;
    std::vector<cv::Point> bottomPoints;
    
    for (int i = 0; i < numBands; ++i) {
        float magnitude = smoothedBands[i] * settings.scale;
        magnitude = std::min(magnitude, 1.0f);
        
        int x = (i * settings.width) / numBands;
        int amplitude = static_cast<int>(magnitude * maxAmplitude);
        
        topPoints.push_back(cv::Point(x, centerY - amplitude));
        bottomPoints.push_back(cv::Point(x, centerY + amplitude));
    }
    
    // Draw filled waveform
    std::vector<cv::Point> allPoints = topPoints;
    allPoints.insert(allPoints.end(), bottomPoints.rbegin(), bottomPoints.rend());
    
    if (allPoints.size() >= 3) {
        cv::fillPoly(frame, allPoints, cv::Scalar(255, 100, 200));
    }
    
    // Draw outline
    if (topPoints.size() >= 2) {
        for (size_t i = 0; i < topPoints.size() - 1; ++i) {
            cv::line(frame, topPoints[i], topPoints[i + 1], cv::Scalar(255, 255, 255), 2);
            cv::line(frame, bottomPoints[i], bottomPoints[i + 1], cv::Scalar(255, 255, 255), 2);
        }
    }
    
    return frame;
}

} // namespace Visualizers
