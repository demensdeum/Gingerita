rm -rfv $(find . -name 'CMakeFiles' -o -name 'cmake_install.cmake')
cmake .
make
cp -vf bin/kf6/ktexteditor/*.so ~/CraftRoot/plugins/kf6/ktexteditor/
