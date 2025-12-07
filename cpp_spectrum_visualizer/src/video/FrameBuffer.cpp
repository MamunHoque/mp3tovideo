/**
 * @file FrameBuffer.cpp
 * @brief Implementation of frame buffer
 */

#include "video/FrameBuffer.h"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <filesystem>

namespace Video {

FrameBuffer::FrameBuffer(const std::string& tempDir)
    : tempDir(tempDir)
    , tempPath(tempDir)
{
    std::filesystem::create_directories(tempPath);
}

FrameBuffer::~FrameBuffer() {
    clear();
    if (std::filesystem::exists(tempPath)) {
        std::filesystem::remove_all(tempPath);
    }
}

std::string FrameBuffer::saveFrame(const cv::Mat& frame, int frameNumber) {
    std::ostringstream oss;
    oss << "frame_" << std::setfill('0') << std::setw(6) << frameNumber << ".png";
    std::string filename = oss.str();
    std::filesystem::path filepath = tempPath / filename;
    
    cv::imwrite(filepath.string(), frame);
    return filepath.string();
}

std::string FrameBuffer::getFramePath(int frameNumber) const {
    std::ostringstream oss;
    oss << "frame_" << std::setfill('0') << std::setw(6) << frameNumber << ".png";
    std::string filename = oss.str();
    std::filesystem::path filepath = tempPath / filename;
    return filepath.string();
}

void FrameBuffer::clear() {
    if (std::filesystem::exists(tempPath)) {
        for (const auto& entry : std::filesystem::directory_iterator(tempPath)) {
            if (entry.is_regular_file() && entry.path().extension() == ".png") {
                std::filesystem::remove(entry.path());
            }
        }
    }
}

bool FrameBuffer::frameExists(int frameNumber) const {
    return std::filesystem::exists(getFramePath(frameNumber));
}

} // namespace Video
