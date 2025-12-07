#!/bin/bash

# Build script for macOS
# This script builds the MP3 Spectrum Visualizer application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
INSTALL_DIR="${SCRIPT_DIR}/install"

echo "=== MP3 Spectrum Visualizer Build Script ==="
echo "Build directory: ${BUILD_DIR}"
echo ""

# Check for required dependencies
echo "Checking dependencies..."
MISSING_DEPS=()

if ! brew list qt >/dev/null 2>&1 && ! brew list qt@6 >/dev/null 2>&1; then
    MISSING_DEPS+=("qt@6")
fi

if ! brew list opencv >/dev/null 2>&1; then
    MISSING_DEPS+=("opencv")
fi

if ! brew list fftw >/dev/null 2>&1; then
    MISSING_DEPS+=("fftw")
fi

if ! brew list pkg-config >/dev/null 2>&1; then
    MISSING_DEPS+=("pkg-config")
fi

if ! brew list libsndfile >/dev/null 2>&1; then
    MISSING_DEPS+=("libsndfile")
fi

# Check for ffmpeg binary in PATH (not a library dependency)
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: ffmpeg binary not found in PATH"
    echo "Install with: brew install ffmpeg"
    echo "FFmpeg is required for video encoding at runtime"
    echo ""
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "WARNING: Missing build dependencies: ${MISSING_DEPS[*]}"
    echo "Install them with: brew install ${MISSING_DEPS[*]}"
    echo ""
    echo "Attempting to continue anyway (installation may be in progress)..."
    echo ""
else
    echo "All build dependencies found!"
    echo ""
fi

# Clean previous build
if [ -d "${BUILD_DIR}" ]; then
    echo "Cleaning previous build..."
    rm -rf "${BUILD_DIR}"
fi

mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Find Homebrew prefix and Qt6
HOMEBREW_PREFIX=$(brew --prefix)
QT6_PATH="${HOMEBREW_PREFIX}/opt/qt@6"
if [ ! -d "${QT6_PATH}" ]; then
    QT6_PATH="${HOMEBREW_PREFIX}/opt/qt"
fi

# Set CMAKE_PREFIX_PATH to include Homebrew packages
CMAKE_PREFIX_PATH="${HOMEBREW_PREFIX}:${QT6_PATH}"
if [ -d "${QT6_PATH}" ]; then
    echo "Found Qt6 at: ${QT6_PATH}"
else
    echo "Warning: Qt6 not found. Make sure qt@6 is installed: brew install qt@6"
fi

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    OSX_ARCHS="arm64"
else
    OSX_ARCHS="x86_64"
fi

# Configure CMake
echo "Configuring CMake..."
echo "CMAKE_PREFIX_PATH: ${CMAKE_PREFIX_PATH}"
echo "Building for architecture: ${OSX_ARCHS}"
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_ARCHITECTURES="${OSX_ARCHS}" \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0 \
    -DCMAKE_PREFIX_PATH="${CMAKE_PREFIX_PATH}"

# Build
echo ""
echo "Building..."
cmake --build . --config Release --parallel

echo ""
echo "=== Build Complete ==="
echo "Executable: ${BUILD_DIR}/Release/SpectrumVisualizer.app"
echo ""
echo "To run:"
echo "  cd ${BUILD_DIR}"
echo "  ./Release/SpectrumVisualizer.app/Contents/MacOS/SpectrumVisualizer"
echo ""
