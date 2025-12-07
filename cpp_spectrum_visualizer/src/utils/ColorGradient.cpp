/**
 * @file ColorGradient.cpp
 * @brief Implementation of ColorGradient class
 */

#include "utils/ColorGradient.h"
#include <cmath>
#include <algorithm>

namespace Utils {

ColorGradient::ColorGradient(GradientType type)
    : gradientType(type)
    , customStart(255, 0, 255, 255)
    , customEnd(0, 255, 255, 255)
    , monoColor(255, 255, 255, 255)
{
}

cv::Scalar ColorGradient::getColor(int index, int total, float magnitude) const
{
    magnitude = std::clamp(magnitude, 0.0f, 1.0f);
    
    switch (gradientType) {
        case GradientType::PitchRainbow:
            return pitchRainbowColor(index, total, magnitude);
        case GradientType::FrequencyBased:
            return frequencyBasedColor(index, total, magnitude);
        case GradientType::EnergyBased:
            return energyBasedColor(magnitude);
        case GradientType::Custom:
            return customColor(index, total, magnitude);
        case GradientType::Monochrome:
            return monochromeColor(magnitude);
        default:
            return frequencyBasedColor(index, total, magnitude);
    }
}

cv::Scalar ColorGradient::pitchRainbowColor(int index, int total, float magnitude) const
{
    if (total == 0) return cv::Scalar(0, 0, 0, 255);
    
    // Map index to hue (0-360)
    float hue = (static_cast<float>(index) / total) * 360.0f;
    float h = hue / 60.0f;
    float x = 1.0f - std::abs(std::fmod(h, 2.0f) - 1.0f);
    
    float r, g, b;
    if (h < 1.0f) {
        r = 1.0f; g = x; b = 0.0f;
    } else if (h < 2.0f) {
        r = x; g = 1.0f; b = 0.0f;
    } else if (h < 3.0f) {
        r = 0.0f; g = 1.0f; b = x;
    } else if (h < 4.0f) {
        r = 0.0f; g = x; b = 1.0f;
    } else if (h < 5.0f) {
        r = x; g = 0.0f; b = 1.0f;
    } else {
        r = 1.0f; g = 0.0f; b = x;
    }
    
    // Apply magnitude as brightness
    float brightness = 0.5f + (magnitude * 0.5f);
    r *= brightness * 255.0f;
    g *= brightness * 255.0f;
    b *= brightness * 255.0f;
    
    return cv::Scalar(b, g, r, 255);  // OpenCV uses BGR
}

cv::Scalar ColorGradient::frequencyBasedColor(int index, int total, float magnitude) const
{
    if (total == 0) return cv::Scalar(0, 0, 0, 255);
    
    float r, g, b;
    float third = total / 3.0f;
    float twoThirds = total * 2.0f / 3.0f;
    
    if (index < third) {
        // Low frequency - red to yellow
        r = 255.0f;
        g = 255.0f * (index / third);
        b = 0.0f;
    } else if (index < twoThirds) {
        // Mid frequency - yellow to cyan
        float t = (index - third) / third;
        r = 255.0f * (1.0f - t);
        g = 255.0f;
        b = 255.0f * t;
    } else {
        // High frequency - cyan to blue
        float t = (index - twoThirds) / third;
        r = 0.0f;
        g = 255.0f * (1.0f - t);
        b = 255.0f;
    }
    
    return cv::Scalar(b, g, r, 255);  // OpenCV uses BGR
}

cv::Scalar ColorGradient::energyBasedColor(float magnitude) const
{
    float r, g, b;
    
    if (magnitude < 0.33f) {
        // Blue to green
        r = 0.0f;
        g = magnitude * 3.0f * 255.0f;
        b = 255.0f;
    } else if (magnitude < 0.66f) {
        // Green to red
        float t = (magnitude - 0.33f) * 3.0f;
        r = t * 255.0f;
        g = 255.0f;
        b = (1.0f - t) * 255.0f;
    } else {
        // Red to yellow
        float t = (magnitude - 0.66f) * 3.0f;
        r = 255.0f;
        g = (1.0f - t) * 255.0f;
        b = 0.0f;
    }
    
    return cv::Scalar(b, g, r, 255);  // OpenCV uses BGR
}

cv::Scalar ColorGradient::customColor(int index, int total, float magnitude) const
{
    if (total == 0) return cv::Scalar(0, 0, 0, 255);
    
    float t = static_cast<float>(index) / total;
    
    // Interpolate between start and end colors
    float b = customStart[0] + (customEnd[0] - customStart[0]) * t;
    float g = customStart[1] + (customEnd[1] - customStart[1]) * t;
    float r = customStart[2] + (customEnd[2] - customStart[2]) * t;
    
    // Apply magnitude as brightness
    float brightness = 0.5f + (magnitude * 0.5f);
    r *= brightness;
    g *= brightness;
    b *= brightness;
    
    return cv::Scalar(b, g, r, 255);
}

cv::Scalar ColorGradient::monochromeColor(float magnitude) const
{
    float b = monoColor[0] * magnitude;
    float g = monoColor[1] * magnitude;
    float r = monoColor[2] * magnitude;
    
    return cv::Scalar(b, g, r, 255);
}

void ColorGradient::setCustomColors(const cv::Scalar& start, const cv::Scalar& end)
{
    customStart = start;
    customEnd = end;
}

void ColorGradient::setMonochromeColor(const cv::Scalar& color)
{
    monoColor = color;
}

GradientType ColorGradient::fromString(const std::string& str)
{
    if (str == "pitch_rainbow") return GradientType::PitchRainbow;
    if (str == "frequency-based" || str == "frequency_based") return GradientType::FrequencyBased;
    if (str == "energy-based" || str == "energy_based") return GradientType::EnergyBased;
    if (str == "custom") return GradientType::Custom;
    if (str == "monochrome") return GradientType::Monochrome;
    return GradientType::PitchRainbow; // Default
}

} // namespace Utils
