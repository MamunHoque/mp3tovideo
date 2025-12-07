/**
 * @file BaseVisualizer.cpp
 * @brief Implementation of base visualizer
 */

#include "visualizers/BaseVisualizer.h"
#include "utils/ColorGradient.h"
#include <algorithm>

namespace Visualizers {

BaseVisualizer::BaseVisualizer(const VisualizerSettings& settings)
    : settings(settings)
{
    // Initialize color gradient based on type
    Utils::GradientType gradType = Utils::GradientType::PitchRainbow;
    
    switch (settings.gradientType) {
        case ColorGradientType::PitchRainbow:
            gradType = Utils::GradientType::PitchRainbow;
            break;
        case ColorGradientType::FrequencyBased:
            gradType = Utils::GradientType::FrequencyBased;
            break;
        case ColorGradientType::EnergyBased:
            gradType = Utils::GradientType::EnergyBased;
            break;
        case ColorGradientType::Custom:
            gradType = Utils::GradientType::Custom;
            break;
        case ColorGradientType::Monochrome:
            gradType = Utils::GradientType::Monochrome;
            break;
    }
    
    colorGradient = std::make_unique<Utils::ColorGradient>(gradType);
    
    if (settings.gradientType == ColorGradientType::Custom && settings.customColors.size() >= 2) {
        colorGradient->setCustomColors(settings.customColors[0], settings.customColors[1]);
    }
    
    if (settings.gradientType == ColorGradientType::Monochrome) {
        colorGradient->setMonochromeColor(settings.monochromeColor);
    }
}

cv::Scalar BaseVisualizer::getColor(int bandIndex, int numBands, float magnitude) {
    return colorGradient->getColor(bandIndex, numBands, magnitude);
}

void BaseVisualizer::updateSettings(const VisualizerSettings& newSettings) {
    settings = newSettings;
    
    // Update color gradient
    Utils::GradientType gradType = Utils::GradientType::PitchRainbow;
    switch (settings.gradientType) {
        case ColorGradientType::PitchRainbow: gradType = Utils::GradientType::PitchRainbow; break;
        case ColorGradientType::FrequencyBased: gradType = Utils::GradientType::FrequencyBased; break;
        case ColorGradientType::EnergyBased: gradType = Utils::GradientType::EnergyBased; break;
        case ColorGradientType::Custom: gradType = Utils::GradientType::Custom; break;
        case ColorGradientType::Monochrome: gradType = Utils::GradientType::Monochrome; break;
    }
    colorGradient->setGradientType(gradType);
    
    if (settings.gradientType == ColorGradientType::Custom && settings.customColors.size() >= 2) {
        colorGradient->setCustomColors(settings.customColors[0], settings.customColors[1]);
    }
    if (settings.gradientType == ColorGradientType::Monochrome) {
        colorGradient->setMonochromeColor(settings.monochromeColor);
    }
}

void BaseVisualizer::smoothBands(const std::vector<float>& bands) {
    if (smoothedBands.empty()) {
        smoothedBands = bands;
        return;
    }
    
    if (smoothedBands.size() != bands.size()) {
        smoothedBands.resize(bands.size());
    }
    
    for (size_t i = 0; i < bands.size(); ++i) {
        smoothedBands[i] = smoothedBands[i] * settings.smoothing + 
                          bands[i] * (1.0f - settings.smoothing);
    }
}

} // namespace Visualizers


