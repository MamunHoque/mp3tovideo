/**
 * @file CircleVisualizer.h
 * @brief Circular spectrum analyzer visualizer
 */

#pragma once

#include "visualizers/BaseVisualizer.h"

namespace Visualizers {

/**
 * @class CircleVisualizer
 * @brief Circular spectrum analyzer visualization
 */
class CircleVisualizer : public BaseVisualizer {
public:
    explicit CircleVisualizer(const VisualizerSettings& settings);
    
    cv::Mat render(const std::vector<float>& bands, const cv::Mat& background) override;
};

} // namespace Visualizers
