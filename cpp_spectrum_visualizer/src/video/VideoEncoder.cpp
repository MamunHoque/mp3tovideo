/**
 * @file VideoEncoder.cpp
 * @brief Implementation of video encoder
 */

#include "video/VideoEncoder.h"
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <filesystem>

namespace Video {

VideoEncoder::VideoEncoder(const EncodingSettings& settings)
    : settings(settings)
{
    // Detect hardware acceleration on macOS
    if (settings.useHardwareAccel && settings.hardwareCodec.empty()) {
        #ifdef __APPLE__
        this->settings.hardwareCodec = "h264_videotoolbox";
        #endif
    }
}

bool VideoEncoder::encode(const std::string& frameDir, const std::string& outputPath,
                         const std::string& audioPath) {
    std::string cmd = buildFFmpegCommand(frameDir, outputPath, audioPath);
    
    int result = std::system(cmd.c_str());
    return result == 0;
}

bool VideoEncoder::encodeFromPaths(const std::vector<std::string>& framePaths,
                                   const std::string& outputPath,
                                   const std::string& audioPath) {
    // For now, use frame directory approach
    // Could be optimized to use concat demuxer
    if (framePaths.empty()) {
        return false;
    }
    
    // Use directory of first frame
    std::filesystem::path firstFrame(framePaths[0]);
    std::string frameDir = firstFrame.parent_path().string();
    
    return encode(frameDir, outputPath, audioPath);
}

std::string VideoEncoder::buildFFmpegCommand(const std::string& frameDir,
                                            const std::string& outputPath,
                                            const std::string& audioPath) const {
    std::ostringstream cmd;
    
    cmd << "ffmpeg -y ";  // -y to overwrite output
    
    // Input frames (pattern)
    cmd << "-framerate " << settings.fps << " ";
    cmd << "-pattern_type sequence -start_number 0 ";
    cmd << "-i \"" << frameDir << "/frame_%06d.png\" ";
    
    // Video encoding settings
    if (settings.useHardwareAccel && !settings.hardwareCodec.empty()) {
        cmd << "-c:v " << settings.hardwareCodec << " ";
    } else {
        cmd << "-c:v " << settings.codec << " ";
        cmd << "-preset " << settings.preset << " ";
    }
    
    cmd << "-b:v " << settings.bitrate << " ";
    cmd << "-pix_fmt " << settings.pixelFormat << " ";
    cmd << "-s " << settings.width << "x" << settings.height << " ";
    
    // Audio if provided
    if (!audioPath.empty() && std::filesystem::exists(audioPath)) {
        cmd << "-i \"" << audioPath << "\" ";
        cmd << "-c:a aac -b:a 192k ";
        cmd << "-shortest ";  // Match video length
    }
    
    // Output
    cmd << "\"" << outputPath << "\"";
    
    return cmd.str();
}

} // namespace Video
