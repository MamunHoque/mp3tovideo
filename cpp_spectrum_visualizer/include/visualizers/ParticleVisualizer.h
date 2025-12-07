/**
 * @file ParticleVisualizer.h
 * @brief Audio-reactive particle system visualizer
 */

#pragma once

#include "visualizers/BaseVisualizer.h"
#include <vector>

namespace Visualizers {

/**
 * @struct Particle
 * @brief Particle structure for particle system
 */
struct Particle {
    float x, y;
    float vx, vy;
    float life;
    cv::Scalar color;
};

/**
 * @class ParticleVisualizer
 * @brief Audio-reactive particle system visualization
 */
class ParticleVisualizer : public BaseVisualizer {
public:
    explicit ParticleVisualizer(const VisualizerSettings& settings);
    
    cv::Mat render(const std::vector<float>& bands, const cv::Mat& background) override;

private:
    void updateParticles(const std::vector<float>& bands);
    void spawnParticles(const std::vector<float>& bands);
    
    std::vector<Particle> particles;
    int maxParticles = 500;
    float particleSpeed = 2.0f;
    float particleDecay = 0.95f;
};

} // namespace Visualizers
