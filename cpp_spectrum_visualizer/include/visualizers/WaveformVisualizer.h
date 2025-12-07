/**
 * @file WaveformVisualizer.h
 * @brief Smooth filled waveform visualizer
 */

#pragma once

#include "visualizers/BaseVisualizer.h"

namespace Visualizers {

/**
 * @class WaveformVisualizer
 * @brief Smooth filled waveform visualization
 */
class WaveformVisualizer : public BaseVisualizer {
public:
    explicit WaveformVisualizer(const VisualizerSettings& settings);
    
    cv::Mat render(const std::vector<float>& bands, const cv::Mat& background) override;
};

} // namespace Visualizers
