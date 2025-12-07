/**
 * @file VideoEncoder.h
 * @brief Video encoding using FFmpeg
 */

#pragma once

#include <string>
#include <vector>

namespace Video {

/**
 * @struct EncodingSettings
 * @brief Settings for video encoding
 */
struct EncodingSettings {
    int width = 1920;
    int height = 1080;
    int fps = 30;
    int bitrate = 5000000;  // 5 Mbps
    std::string codec = "libx264";
    std::string preset = "medium";
    std::string pixelFormat = "yuv420p";
    bool useHardwareAccel = false;
    std::string hardwareCodec;
};

/**
 * @class VideoEncoder
 * @brief Encodes frames into video using FFmpeg
 */
class VideoEncoder {
public:
    explicit VideoEncoder(const EncodingSettings& settings);
    
    /**
     * @brief Encode frames from directory into video
     * @param frameDir Directory containing frame images
     * @param outputPath Output video path
     * @param audioPath Optional audio file to mix in
     * @return True if successful
     */
    bool encode(const std::string& frameDir, const std::string& outputPath, 
                const std::string& audioPath = "");
    
    /**
     * @brief Encode frames from list of paths
     * @param framePaths List of frame image paths
     * @param outputPath Output video path
     * @param audioPath Optional audio file to mix in
     * @return True if successful
     */
    bool encodeFromPaths(const std::vector<std::string>& framePaths,
                        const std::string& outputPath,
                        const std::string& audioPath = "");

private:
    EncodingSettings settings;
    std::string buildFFmpegCommand(const std::string& frameDir, 
                                   const std::string& outputPath,
                                   const std::string& audioPath) const;
};

} // namespace Video
