/**
 * @file BackgroundProcessor.h
 * @brief Video background processing
 */

#pragma once

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>
#include <optional>

namespace Effects {

/**
 * @class BackgroundProcessor
 * @brief Handles video background loading and frame extraction
 */
class BackgroundProcessor {
public:
    explicit BackgroundProcessor(const std::string& videoPath, int targetFps = 30);
    ~BackgroundProcessor();
    
    /**
     * @brief Load video file
     * @return True if successful
     */
    bool loadVideo();
    
    /**
     * @brief Get video duration in seconds
     */
    double getDuration() const { return duration; }
    
    /**
     * @brief Cache frames in memory
     * @param maxFrames Maximum frames to cache (0 for all)
     * @return True if successful
     */
    bool cacheFrames(int maxFrames = 0);
    
    /**
     * @brief Get frame at specific time with looping
     * @param timeSeconds Time in seconds
     * @param targetSize Target size for frame
     * @return Frame or empty optional if error
     */
    std::optional<cv::Mat> getFrameAtTime(double timeSeconds, const cv::Size& targetSize);
    
    /**
     * @brief Get frame for specific output frame number
     * @param frameNumber Frame number
     * @param targetSize Target size
     * @return Frame or empty optional if error
     */
    std::optional<cv::Mat> getFrameAtFrameNumber(int frameNumber, const cv::Size& targetSize);
    
    /**
     * @brief Close and release resources
     */
    void close();

private:
    std::optional<cv::Mat> readFrameFromVideo(int frameNumber);
    
    std::string videoPath;
    int targetFps;
    cv::VideoCapture videoCapture;
    double videoFps;
    int totalFrames;
    double duration;
    std::vector<cv::Mat> frameCache;
    bool cacheLoaded;
};

} // namespace Effects
