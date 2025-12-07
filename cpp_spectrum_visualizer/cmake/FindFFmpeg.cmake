# FindFFmpeg.cmake - Find FFmpeg libraries
# This module defines:
#  FFMPEG_FOUND - System has FFmpeg
#  FFMPEG_INCLUDE_DIRS - The FFmpeg include directories
#  FFMPEG_LIBRARIES - The libraries needed to use FFmpeg

set(FFMPEG_COMPONENTS avcodec avformat avutil swscale swresample)

foreach(component ${FFMPEG_COMPONENTS})
    find_path(FFMPEG_${component}_INCLUDE_DIR lib${component}/${component}.h
        HINTS
            /usr/local/include
            /usr/include
            /opt/homebrew/include
            ${FFMPEG_ROOT}/include
    )
    
    find_library(FFMPEG_${component}_LIBRARY
        NAMES ${component} lib${component}
        HINTS
            /usr/local/lib
            /usr/lib
            /opt/homebrew/lib
            ${FFMPEG_ROOT}/lib
    )
    
    if(FFMPEG_${component}_INCLUDE_DIR AND FFMPEG_${component}_LIBRARY)
        list(APPEND FFMPEG_INCLUDE_DIRS ${FFMPEG_${component}_INCLUDE_DIR})
        list(APPEND FFMPEG_LIBRARIES ${FFMPEG_${component}_LIBRARY})
        set(FFMPEG_${component}_FOUND TRUE)
    endif()
endforeach()

list(REMOVE_DUPLICATES FFMPEG_INCLUDE_DIRS)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(FFmpeg
    REQUIRED_VARS FFMPEG_LIBRARIES FFMPEG_INCLUDE_DIRS
    HANDLE_COMPONENTS
)

mark_as_advanced(FFMPEG_INCLUDE_DIRS FFMPEG_LIBRARIES)




