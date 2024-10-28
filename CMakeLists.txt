cmake_minimum_required(VERSION 3.23)
project(zarr-benchmarks)
cmake_policy(SET CMP0057 NEW)
cmake_policy(SET CMP0079 NEW)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Common dependencies
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

# Dependencies for acquire-zarr
find_package(nlohmann_json CONFIG REQUIRED)
find_package(blosc CONFIG REQUIRED)
find_package(miniocpp CONFIG REQUIRED)

include_directories(
    /usr/local/include
    ${Python3_INCLUDE_DIRS}
    ${pybind11_INCLUDE_DIR}
)

# construct bindings for cppZarr
find_library(cppZarrLib cppZarr REQUIRED)
pybind11_add_module(pyCppZarr zarr_libraries/cpp_zarr/cpp_zarr.cpp)
target_link_libraries(pyCppZarr PRIVATE ${cppZarrLib})

# build acquire-zarr
set(BUILD_PYTHON ON CACHE BOOL "Build Python bindings for acquire-zarr")
set(BUILD_TESTING OFF CACHE BOOL "Disable acquire-zarr tests")
add_subdirectory(external/acquire-zarr)

add_custom_target(install-acquire-zarr-python
    COMMAND ${Python3_EXECUTABLE} -m pip install .
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/external/acquire-zarr
    DEPENDS acquire-zarr
    COMMENT "Installing acquire-zarr Python package"
)

# Make the Python installation part of the default build
add_dependencies(pyCppZarr install-acquire-zarr-python)

# Installation rules
install(TARGETS pyCppZarr
        LIBRARY DESTINATION ${Python3_SITEARCH}/zarr_benchmarks
        RUNTIME DESTINATION ${Python3_SITEARCH}/zarr_benchmarks)