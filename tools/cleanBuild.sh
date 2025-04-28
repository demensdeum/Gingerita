#!/bin/bash

if [ -z "$KDEROOT" ]; then
    echo "Error: Craft environment is not loaded. Please run 'source ~/CraftRoot/craft/craftenv.sh' first."
    exit 1
fi

rm -rfv ~/Sources/DemensDeum/Gingerita/bin/kate.app

rm -rfv $(find . -name 'CMakeFiles' -o -name 'cmake_install.cmake')
cmake -DCMAKE_BUILD_TYPE=Debug .
make
