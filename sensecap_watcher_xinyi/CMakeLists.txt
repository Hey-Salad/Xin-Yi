# CMakeLists.txt for SenseCAP Watcher Xin-Yi Firmware
# ESP-IDF 5.4+ Required

cmake_minimum_required(VERSION 3.16)

# Set the components search directories
set(EXTRA_COMPONENT_DIRS
    ${CMAKE_CURRENT_LIST_DIR}/components
)

# Include the ESP-IDF CMake project
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Define the project
project(sensecap_watcher_xinyi)
