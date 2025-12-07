/**
 * @file BaseVisualizer.h
 * @brief Base class for all visualizers
 */

#pragma once

#include <opencv2/opencv.hpp>
#include <vector>
#include <string>
#include "utils/ColorGradient.h"

namespace Visualizers {

/**
 * @enum ColorGradientType
 * @brief Types of color gradients
 */
enum class ColorGradientType {
    PitchRainbow,      // Full spectrum rainbow
    FrequencyBased,    // Low=red, mid=green, high=blue
    EnergyBased,       // Color intensity based on amplitude
    Custom,            // User-defined gradient
    Monochrome         // Single color with varying intensity
};

/**
 * @struct VisualizerSettings
 * @brief Settings for visualizer rendering
 */
struct VisualizerSettings {
    int width = 1920;
    int height = 1080;
    ColorGradientType gradientType = ColorGradientType::PitchRainbow;
    std::vector<cv::Scalar> customColors;
    cv::Scalar monochromeColor = cv::Scalar(255, 0, 255);
    float smoothing = 0.7f;
    float scale = 1.0f;
};

/**
 * @class BaseVisualizer
 * @brief Base class for all spectrum visualizers
 */
class BaseVisualizer {
public:
    explicit BaseVisualizer(const VisualizerSettings& settings);
    virtual ~BaseVisualizer() = default;
    
    /**
     * @brief Render visualization frame
     * @param bands Frequency band magnitudes (0.0 to 1.0)
     * @param background Background image (will be copied)
     * @return Rendered frame
     */
    virtual cv::Mat render(const std::vector<float>& bands, const cv::Mat& background) = 0;
    
    /**
     * @brief Get color for a frequency band
     * @param bandIndex Band index
     * @param numBands Total number of bands
     * @param magnitude Band magnitude (0.0 to 1.0)
     * @return BGR color
     */
    cv::Scalar getColor(int bandIndex, int numBands, float magnitude);
    
    /**
     * @brief Update settings
     * @param settings New settings
     */
    void updateSettings(const VisualizerSettings& settings);

protected:
    VisualizerSettings settings;
    Utils::ColorGradient colorGradient;
    std::vector<float> smoothedBands;
    
    void smoothBands(const std::vector<float>& bands);
};

} // namespace Visualizers
