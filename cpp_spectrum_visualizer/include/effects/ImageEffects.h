/**
 * @file ImageEffects.h
 * @brief Image processing effects (blur, vignette, etc.)
 */

#pragma once

#include <opencv2/opencv.hpp>
#include <string>

namespace Effects {

/**
 * @brief Apply Gaussian blur to an image
 * @param image Input image
 * @param intensity Blur intensity (0.0 to 100.0)
 * @return Blurred image
 */
cv::Mat applyBlur(const cv::Mat& image, float intensity);

/**
 * @brief Apply vignette effect (darken edges)
 * @param image Input image
 * @param intensity Vignette intensity (0.0 to 100.0)
 * @return Image with vignette
 */
cv::Mat applyVignette(const cv::Mat& image, float intensity);

/**
 * @brief Convert image to grayscale
 * @param image Input image
 * @return Grayscale image
 */
cv::Mat applyBlackAndWhite(const cv::Mat& image);

/**
 * @brief Fit background image to canvas size
 * @param image Input image
 * @param canvasSize Target size (width, height)
 * @param mode Fit mode: "stretch", "tile", "center"
 * @return Fitted image
 */
cv::Mat fitBackground(const cv::Mat& image, const cv::Size& canvasSize, const std::string& mode);

/**
 * @brief Apply fade-in effect
 * @param baseImage Base image
 * @param frameNumber Current frame number
 * @param totalFrames Total frames for fade-in
 * @return Faded image
 */
cv::Mat applyFadeIn(const cv::Mat& baseImage, int frameNumber, int totalFrames);

} // namespace Effects
