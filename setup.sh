#!/bin/bash

BUILD_DIR="build"

# check if the directory exists
if [ -d "$BUILD_DIR" ]; then
  echo "Directory '$BUILD_DIR' exists. Deleting it..."
  rm -rf "$BUILD_DIR"
else
  echo "Directory '$BUILD_DIR' does not exist. No need to delete."
fi

# create a new directory
echo "Creating a new '$BUILD_DIR' directory..."
mkdir "$BUILD_DIR"

echo "Directory '$BUILD_DIR' has been created successfully."

# build cpp code 
cd "$BUILD_DIR" || { echo "Failed to change directory to '$BUILD_DIR'"; exit 1; }
cmake --preset=default .. || { echo "Failed to run cmake '$BUILD_DIR'"; exit 1; }
make || { echo "Failed to run make"; exit 1; }

echo "Build process completed successfully."