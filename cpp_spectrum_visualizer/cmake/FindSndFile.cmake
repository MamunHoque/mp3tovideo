# FindSndFile.cmake - Find libsndfile library
# This module defines:
#  SNDFILE_FOUND - System has libsndfile
#  SNDFILE_INCLUDE_DIRS - The libsndfile include directories
#  SNDFILE_LIBRARIES - The libraries needed to use libsndfile

find_path(SNDFILE_INCLUDE_DIR sndfile.h
    HINTS
        /usr/local/include
        /usr/include
        /opt/homebrew/include
        ${SNDFILE_ROOT}/include
)

find_library(SNDFILE_LIBRARY
    NAMES sndfile libsndfile
    HINTS
        /usr/local/lib
        /usr/lib
        /opt/homebrew/lib
        ${SNDFILE_ROOT}/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(SndFile
    REQUIRED_VARS SNDFILE_LIBRARY SNDFILE_INCLUDE_DIR
)

if(SNDFILE_FOUND)
    set(SNDFILE_LIBRARIES ${SNDFILE_LIBRARY})
    set(SNDFILE_INCLUDE_DIRS ${SNDFILE_INCLUDE_DIR})
endif()

mark_as_advanced(SNDFILE_INCLUDE_DIR SNDFILE_LIBRARY)




