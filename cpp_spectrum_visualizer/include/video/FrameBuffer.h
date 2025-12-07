/**
 * @file FrameBuffer.h
 * @brief Frame buffer for temporary frame storage
 */

#pragma once

#include <opencv2/opencv.hpp>
#include <vector>
#include <string>
#include <filesystem>

namespace Video {

/**
 * @class FrameBuffer
 * @brief Manages temporary frame storage during video generation
 */
class FrameBuffer {
public:
    explicit FrameBuffer(const std::string& tempDir);
    ~FrameBuffer();
    
    /**
     * @brief Save frame to disk
     * @param frame Frame to save
     * @param frameNumber Frame number (for filename)
     * @return Path to saved frame
     */
    std::string saveFrame(const cv::Mat& frame, int frameNumber);
    
    /**
     * @brief Get path to frame file
     * @param frameNumber Frame number
     * @return Path to frame file
     */
    std::string getFramePath(int frameNumber) const;
    
    /**
     * @brief Clear all saved frames
     */
    void clear();
    
    /**
     * @brief Get temporary directory path
     */
    std::string getTempDir() const { return tempDir; }
    
    /**
     * @brief Check if frame exists
     */
    bool frameExists(int frameNumber) const;

private:
    std::string tempDir;
    std::filesystem::path tempPath;
};

} // namespace Video
