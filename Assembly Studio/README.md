# Assembly Vault

Personal x86-64 assembly projects, written with NASM syntax and aimed at Linux (Debian). The school course uses GAS, so this space is for projects outside of class.

## Projects

| File | Description |
| --- | --- |
| `hello_world.asm` | Prints "Hello, World!" with two raw Linux system calls. |

## Build and run (Debian)

```bash
nasm -f elf64 hello_world.asm -o hello_world.o
ld hello_world.o -o hello_world
./hello_world
```

Not running Debian? On Windows, use WSL to follow the same steps.
