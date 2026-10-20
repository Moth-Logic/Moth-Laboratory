# C++ Forge

Workshop for C++20 projects, experiments and utilities. Built mostly with Visual Studio on Windows, with g++ as a fallback on Debian.

## Projects

| File | Description |
| --- | --- |
| `hello_world.cpp` | Starting point: prints a greeting to the console. |

## Build and run

```bash
g++ -std=c++20 -Wall -Wextra hello_world.cpp -o hello_world
./hello_world
```

On Windows with Visual Studio's developer prompt:

```bat
cl /EHsc /std:c++20 hello_world.cpp
hello_world.exe
```
