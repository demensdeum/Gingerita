rm -rfv $(find . -name 'CMakeFiles' -o -name 'cmake_install.cmake')
cmake .
make
