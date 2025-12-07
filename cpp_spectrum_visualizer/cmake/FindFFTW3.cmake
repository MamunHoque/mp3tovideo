# FindFFTW3.cmake - Find FFTW3 library
# This module defines:
#  FFTW3_FOUND - System has FFTW3
#  FFTW3_INCLUDE_DIRS - The FFTW3 include directories
#  FFTW3_LIBRARIES - The libraries needed to use FFTW3

find_path(FFTW3_INCLUDE_DIR fftw3.h
    HINTS
        /usr/local/include
        /usr/include
        /opt/homebrew/include
        ${FFTW3_ROOT}/include
)

find_library(FFTW3_LIBRARY
    NAMES fftw3 libfftw3
    HINTS
        /usr/local/lib
        /usr/lib
        /opt/homebrew/lib
        ${FFTW3_ROOT}/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(FFTW3
    REQUIRED_VARS FFTW3_LIBRARY FFTW3_INCLUDE_DIR
)

if(FFTW3_FOUND)
    set(FFTW3_LIBRARIES ${FFTW3_LIBRARY})
    set(FFTW3_INCLUDE_DIRS ${FFTW3_INCLUDE_DIR})
endif()

mark_as_advanced(FFTW3_INCLUDE_DIR FFTW3_LIBRARY)
