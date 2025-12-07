/**
 * @file WaveformVisualizer.h
 * @brief Waveform visualizer
 */

#pragma once

#include "visualizers/BaseVisualizer.h"

namespace Visualizers {

class WaveformVisualizer : public BaseVisualizer {
public:
    explicit WaveformVisualizer(const VisualizerSettings& settings);
    
    cv::Mat render(const std::vector<float>& bands, const cv::Mat& background) override;
};

} // namespace Visualizers
