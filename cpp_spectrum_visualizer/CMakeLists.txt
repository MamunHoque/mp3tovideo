cmake_minimum_required(VERSION 3.20)
project(SpectrumVisualizer VERSION 1.0.0 LANGUAGES CXX)

# C++20 Standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Export compile commands for IDEs
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Add cmake modules path
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

# Optimization flags for Release builds
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(MSVC)
        add_compile_options(/O2)
    elseif(APPLE AND CMAKE_SYSTEM_PROCESSOR MATCHES "arm64")
        # Apple Silicon (M1/M2/M3) optimization
        add_compile_options(-O3 -mcpu=apple-m1 -ffast-math)
    else()
        # Intel/AMD x86_64 optimization
        add_compile_options(-O3 -march=native -ffast-math)
    endif()
endif()

# Find required packages
find_package(Qt6 REQUIRED COMPONENTS Widgets Core Gui)
find_package(OpenCV REQUIRED)
find_package(FFTW3 REQUIRED)
find_package(SndFile REQUIRED)
find_package(OpenMP)

# Enable Qt MOC, UIC, and RCC
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${Qt6Widgets_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
    ${FFTW3_INCLUDE_DIRS}
    ${SNDFILE_INCLUDE_DIRS}
)

# Source files
set(SOURCES
    src/main.cpp
    src/audio/AudioProcessor.cpp
    src/audio/BeatDetector.cpp
    src/video/VideoGenerator.cpp
    src/video/FrameBuffer.cpp
    src/video/VideoEncoder.cpp
    src/effects/ImageEffects.cpp
    src/effects/BeatEffects.cpp
    src/effects/BackgroundProcessor.cpp
    src/visualizers/BaseVisualizer.cpp
    src/visualizers/BarsVisualizer.cpp
    src/visualizers/WaveformVisualizer.cpp
    src/visualizers/CircleVisualizer.cpp
    src/visualizers/ParticleVisualizer.cpp
    src/gui/MainWindow.cpp
    src/gui/PreviewWidget.cpp
    src/gui/SettingsManager.cpp
    src/utils/ThreadPool.cpp
    src/utils/ColorGradient.cpp
    src/utils/PerformanceTimer.cpp
)

# Header files
set(HEADERS
    include/audio/AudioProcessor.h
    include/audio/BeatDetector.h
    include/video/VideoGenerator.h
    include/video/FrameBuffer.h
    include/video/VideoEncoder.h
    include/effects/ImageEffects.h
    include/effects/BeatEffects.h
    include/effects/BackgroundProcessor.h
    include/visualizers/BaseVisualizer.h
    include/visualizers/BarsVisualizer.h
    include/visualizers/WaveformVisualizer.h
    include/visualizers/CircleVisualizer.h
    include/visualizers/ParticleVisualizer.h
    include/gui/MainWindow.h
    include/gui/PreviewWidget.h
    include/gui/SettingsManager.h
    include/utils/ThreadPool.h
    include/utils/ColorGradient.h
    include/utils/PerformanceTimer.h
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# Link libraries
target_link_libraries(${PROJECT_NAME}
    Qt6::Widgets
    Qt6::Core
    Qt6::Gui
    ${OpenCV_LIBS}
    ${FFTW3_LIBRARIES}
    ${SNDFILE_LIBRARIES}
)

# Link OpenMP if available
if(OpenMP_CXX_FOUND)
    target_link_libraries(${PROJECT_NAME} OpenMP::OpenMP_CXX)
endif()

# Platform-specific settings
if(APPLE)
    # macOS-specific settings
    set_target_properties(${PROJECT_NAME} PROPERTIES
        MACOSX_BUNDLE TRUE
        MACOSX_BUNDLE_GUI_IDENTIFIER "com.spectrumvisualizer.app"
        MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
        MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    )
    # Link VideoToolbox for hardware encoding
    target_link_libraries(${PROJECT_NAME} "-framework VideoToolbox" "-framework CoreMedia" "-framework CoreVideo")
elseif(WIN32)
    # Windows-specific settings
    set_target_properties(${PROJECT_NAME} PROPERTIES WIN32_EXECUTABLE TRUE)
endif()

# Install targets
install(TARGETS ${PROJECT_NAME}
    BUNDLE DESTINATION .
    RUNTIME DESTINATION bin
)

# Print configuration summary
message(STATUS "")
message(STATUS "=== Spectrum Visualizer Configuration ===")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Qt6 version: ${Qt6_VERSION}")
message(STATUS "OpenCV version: ${OpenCV_VERSION}")
message(STATUS "FFTW3 found: ${FFTW3_FOUND}")
message(STATUS "SndFile found: ${SNDFILE_FOUND}")
message(STATUS "OpenMP found: ${OpenMP_CXX_FOUND}")
message(STATUS "Note: FFmpeg binary required in PATH for video encoding")
message(STATUS "=========================================")
message(STATUS "")




