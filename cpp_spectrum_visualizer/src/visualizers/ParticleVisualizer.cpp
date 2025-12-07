/**
 * @file ParticleVisualizer.cpp
 * @brief Implementation of particle visualizer
 */

#include "visualizers/ParticleVisualizer.h"
#include <algorithm>
#include <random>
#include <cmath>

namespace Visualizers {

ParticleVisualizer::ParticleVisualizer(const VisualizerSettings& settings)
    : BaseVisualizer(settings)
{
    particles.reserve(maxParticles);
}

cv::Mat ParticleVisualizer::render(const std::vector<float>& bands, const cv::Mat& background) {
    cv::Mat frame;
    background.copyTo(frame);
    
    if (bands.empty()) {
        return frame;
    }
    
    smoothBands(bands);
    const auto& bandsToRender = smoothedBands.empty() ? bands : smoothedBands;
    
    // Update and spawn particles
    updateParticles(bandsToRender);
    spawnParticles(bandsToRender);
    
    // Draw particles
    for (const auto& particle : particles) {
        if (particle.life > 0.0f) {
            int radius = static_cast<int>(particle.life * 3);
            cv::circle(frame,
                      cv::Point(static_cast<int>(particle.x), static_cast<int>(particle.y)),
                      radius,
                      particle.color,
                      -1);
        }
    }
    
    return frame;
}

void ParticleVisualizer::updateParticles(const std::vector<float>& bands) {
    for (auto& particle : particles) {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;
        
        // Apply gravity
        particle.vy += 0.2f;
        
        // Decay life
        particle.life *= particleDecay;
        
        // Wrap around screen
        if (particle.x < 0) particle.x = settings.width;
        if (particle.x > settings.width) particle.x = 0;
        if (particle.y > settings.height) {
            particle.y = 0;
            particle.vy = -particleSpeed;
        }
    }
    
    // Remove dead particles
    particles.erase(
        std::remove_if(particles.begin(), particles.end(),
                      [](const Particle& p) { return p.life <= 0.01f; }),
        particles.end()
    );
}

void ParticleVisualizer::spawnParticles(const std::vector<float>& bands) {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_real_distribution<float> disX(0.0f, 1.0f);
    static std::uniform_real_distribution<float> disY(0.0f, 1.0f);
    static std::uniform_real_distribution<float> disAngle(0.0f, 2.0f * M_PI);
    static std::uniform_real_distribution<float> disSpeed(0.5f, particleSpeed);
    
    if (bands.empty()) return;
    
    // Calculate average energy
    float avgEnergy = 0.0f;
    for (float band : bands) {
        avgEnergy += band;
    }
    avgEnergy /= bands.size();
    
    // Spawn particles based on energy
    int particlesToSpawn = static_cast<int>(avgEnergy * 10);
    particlesToSpawn = std::min(particlesToSpawn, maxParticles - static_cast<int>(particles.size()));
    
    for (int i = 0; i < particlesToSpawn; ++i) {
        Particle particle;
        particle.x = disX(gen) * settings.width;
        particle.y = disY(gen) * settings.height;
        
        float angle = disAngle(gen);
        float speed = disSpeed(gen);
        particle.vx = std::cos(angle) * speed;
        particle.vy = std::sin(angle) * speed;
        
        particle.life = 1.0f;
        
        // Assign color based on position
        int bandIndex = static_cast<int>((particle.x / settings.width) * bands.size());
        bandIndex = std::clamp(bandIndex, 0, static_cast<int>(bands.size()) - 1);
        particle.color = getColor(bandIndex, static_cast<int>(bands.size()), bands[bandIndex]);
        
        particles.push_back(particle);
    }
}

} // namespace Visualizers
