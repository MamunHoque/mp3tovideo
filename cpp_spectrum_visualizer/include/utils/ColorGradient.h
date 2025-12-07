/**
 * @file ColorGradient.h
 * @brief Color gradient calculations for visualizers
 */

#pragma once

#include <opencv2/core.hpp>
#include <string>
#include <array>

namespace Utils {

/**
 * @enum GradientType
 * @brief Types of color gradients available
 */
enum class GradientType {
    PitchRainbow,      ///< Rainbow spectrum based on pitch/frequency
    FrequencyBased,    ///< Low=red, mid=green, high=blue
    EnergyBased,       ///< Color based on energy/amplitude
    Custom,            ///< Custom gradient between two colors
    Monochrome         ///< Single color with varying intensity
};

/**
 * @class ColorGradient
 * @brief Utility class for generating color gradients
 */
class ColorGradient {
public:
    /**
     * @brief Constructor
     * @param type Gradient type
     */
    explicit ColorGradient(GradientType type = GradientType::PitchRainbow);
    
    /**
     * @brief Get color for a specific index and magnitude
     * @param index Current index in the spectrum
     * @param total Total number of elements
     * @param magnitude Magnitude value (0.0 to 1.0)
     * @return RGBA color as cv::Scalar
     */
    cv::Scalar getColor(int index, int total, float magnitude) const;
    
    /**
     * @brief Set gradient type
     * @param type New gradient type
     */
    void setGradientType(GradientType type) { gradientType = type; }
    
    /**
     * @brief Set custom gradient colors
     * @param start Start color (RGB)
     * @param end End color (RGB)
     */
    void setCustomColors(const cv::Scalar& start, const cv::Scalar& end);
    
    /**
     * @brief Set monochrome color
     * @param color Base color (RGB)
     */
    void setMonochromeColor(const cv::Scalar& color);
    
    /**
     * @brief Convert gradient type from string
     * @param str String representation
     * @return Gradient type
     */
    static GradientType fromString(const std::string& str);

private:
    cv::Scalar pitchRainbowColor(int index, int total, float magnitude) const;
    cv::Scalar frequencyBasedColor(int index, int total, float magnitude) const;
    cv::Scalar energyBasedColor(float magnitude) const;
    cv::Scalar customColor(int index, int total, float magnitude) const;
    cv::Scalar monochromeColor(float magnitude) const;
    
    GradientType gradientType;
    cv::Scalar customStart;
    cv::Scalar customEnd;
    cv::Scalar monoColor;
};

} // namespace Utils
