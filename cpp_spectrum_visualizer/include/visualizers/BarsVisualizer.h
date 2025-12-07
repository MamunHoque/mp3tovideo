/**
 * @file BarsVisualizer.h
 * @brief Classic spectrum bars visualizer
 */

#pragma once

#include "visualizers/BaseVisualizer.h"

namespace Visualizers {

class BarsVisualizer : public BaseVisualizer {
public:
    explicit BarsVisualizer(const VisualizerSettings& settings);
    
    cv::Mat render(const std::vector<float>& bands, const cv::Mat& background) override;
    
private:
    int barWidth;
    int barSpacing;
};

} // namespace Visualizers
