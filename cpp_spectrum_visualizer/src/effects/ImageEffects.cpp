/**
 * @file ImageEffects.cpp
 * @brief Implementation of image effects
 */

#include "effects/ImageEffects.h"
#include <algorithm>
#include <cmath>

namespace Effects {

cv::Mat applyBlur(const cv::Mat& image, float intensity) {
    if (intensity <= 0.0f) {
        return image.clone();
    }
    
    // Convert intensity (0-100) to kernel size (must be odd)
    int radius = static_cast<int>(intensity / 5.0f);
    int kernelSize = (radius * 2) + 1;
    if (kernelSize % 2 == 0) kernelSize++;
    
    cv::Mat blurred;
    cv::GaussianBlur(image, blurred, cv::Size(kernelSize, kernelSize), 0);
    return blurred;
}

cv::Mat applyVignette(const cv::Mat& image, float intensity) {
    if (intensity <= 0.0f) {
        return image.clone();
    }
    
    cv::Mat result = image.clone();
    int width = image.cols;
    int height = image.rows;
    
    float centerX = width / 2.0f;
    float centerY = height / 2.0f;
    float maxDistance = std::sqrt(centerX * centerX + centerY * centerY);
    
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            float distance = std::sqrt((x - centerX) * (x - centerX) + 
                                      (y - centerY) * (y - centerY));
            float mask = 1.0f - (distance / maxDistance) * (intensity / 100.0f);
            mask = std::clamp(mask, 0.0f, 1.0f);
            
            cv::Vec3b& pixel = result.at<cv::Vec3b>(y, x);
            pixel[0] = static_cast<uchar>(pixel[0] * mask);
            pixel[1] = static_cast<uchar>(pixel[1] * mask);
            pixel[2] = static_cast<uchar>(pixel[2] * mask);
        }
    }
    
    return result;
}

cv::Mat applyBlackAndWhite(const cv::Mat& image) {
    cv::Mat gray;
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    
    cv::Mat bgr;
    cv::cvtColor(gray, bgr, cv::COLOR_GRAY2BGR);
    return bgr;
}

cv::Mat fitBackground(const cv::Mat& image, const cv::Size& canvasSize, const std::string& mode) {
    if (mode == "stretch") {
        cv::Mat resized;
        cv::resize(image, resized, canvasSize, 0, 0, cv::INTER_LANCZOS4);
        return resized;
    }
    else if (mode == "tile") {
        cv::Mat tiled(canvasSize, image.type());
        for (int y = 0; y < canvasSize.height; y += image.rows) {
            for (int x = 0; x < canvasSize.width; x += image.cols) {
                cv::Rect roi(x, y, 
                           std::min(image.cols, canvasSize.width - x),
                           std::min(image.rows, canvasSize.height - y));
                cv::Mat roiMat = tiled(roi);
                cv::Mat srcRoi = image(cv::Rect(0, 0, roi.width, roi.height));
                srcRoi.copyTo(roiMat);
            }
        }
        return tiled;
    }
    else if (mode == "center") {
        // Calculate scale to fit within canvas
        float scale = std::min(static_cast<float>(canvasSize.width) / image.cols,
                              static_cast<float>(canvasSize.height) / image.rows);
        
        int newWidth = static_cast<int>(image.cols * scale);
        int newHeight = static_cast<int>(image.rows * scale);
        
        cv::Mat resized;
        cv::resize(image, resized, cv::Size(newWidth, newHeight), 0, 0, cv::INTER_LANCZOS4);
        
        // Create canvas and center image
        cv::Mat canvas = cv::Mat::zeros(canvasSize, image.type());
        int xOffset = (canvasSize.width - newWidth) / 2;
        int yOffset = (canvasSize.height - newHeight) / 2;
        
        cv::Rect roi(xOffset, yOffset, newWidth, newHeight);
        resized.copyTo(canvas(roi));
        
        return canvas;
    }
    
    // Default to stretch
    cv::Mat resized;
    cv::resize(image, resized, canvasSize, 0, 0, cv::INTER_LANCZOS4);
    return resized;
}

cv::Mat applyFadeIn(const cv::Mat& baseImage, int frameNumber, int totalFrames) {
    if (totalFrames <= 0 || frameNumber >= totalFrames) {
        return baseImage.clone();
    }
    
    float alpha = std::min(1.0f, static_cast<float>(frameNumber) / totalFrames);
    
    if (alpha >= 1.0f) {
        return baseImage.clone();
    }
    
    // Create black background
    cv::Mat black = cv::Mat::zeros(baseImage.size(), baseImage.type());
    
    // Blend
    cv::Mat faded;
    cv::addWeighted(black, 1.0f - alpha, baseImage, alpha, 0.0, faded);
    
    return faded;
}

} // namespace Effects
