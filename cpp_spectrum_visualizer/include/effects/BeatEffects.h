/**
 * @file BeatEffects.h
 * @brief Beat-synchronized visual effects
 */

#pragma once

#include <opencv2/opencv.hpp>

namespace Effects {

/**
 * @brief Apply pulse effect on beats by scaling
 * @param frame Input frame
 * @param beatStrength Beat strength (0.0 to 1.0)
 * @param scaleFactor Maximum scale factor at full beat strength
 * @return Pulsed frame
 */
cv::Mat applyBeatPulse(const cv::Mat& frame, float beatStrength, float scaleFactor = 1.1f);

/**
 * @brief Apply flash effect on beats
 * @param frame Input frame
 * @param beatStrength Beat strength (0.0 to 1.0)
 * @param color BGR color for flash
 * @param maxIntensity Maximum flash intensity
 * @return Flashed frame
 */
cv::Mat applyBeatFlash(const cv::Mat& frame, float beatStrength, 
                      const cv::Scalar& color = cv::Scalar(255, 255, 255),
                      float maxIntensity = 0.3f);

/**
 * @brief Apply strobe effect synchronized to beats
 * @param frame Input frame
 * @param beatStrength Beat strength (0.0 to 1.0)
 * @param color BGR color for strobe
 * @param threshold Minimum beat strength to trigger strobe
 * @return Strobed frame
 */
cv::Mat applyBeatStrobe(const cv::Mat& frame, float beatStrength,
                       const cv::Scalar& color = cv::Scalar(255, 255, 255),
                       float threshold = 0.5f);

/**
 * @brief Apply zoom effect on beats
 * @param frame Input frame
 * @param beatStrength Beat strength (0.0 to 1.0)
 * @param zoomAmount Amount to zoom (0.0 to 1.0)
 * @return Zoomed frame
 */
cv::Mat applyBeatZoom(const cv::Mat& frame, float beatStrength, float zoomAmount = 0.05f);

} // namespace Effects
