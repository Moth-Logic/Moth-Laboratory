; Hello World in x86-64 assembly (NASM, Linux)
; Build:
;   nasm -f elf64 hello_world.asm -o hello_world.o
;   ld hello_world.o -o hello_world
;   ./hello_world
;
; The program talks to the kernel with two system calls:
;   write (rax = 1)  prints the message to stdout (fd 1)
;   exit  (rax = 60) ends the process with status 0

section .data
    msg db "Hello, World!", 10      ; 10 is the newline character
    len equ $ - msg                 ; length of msg, computed by the assembler

section .text
    global _start                   ; entry point for the linker

_start:
    mov rax, 1                      ; syscall number: write
    mov rdi, 1                      ; file descriptor: stdout
    mov rsi, msg                    ; address of the buffer
    mov rdx, len                    ; number of bytes to write
    syscall

    mov rax, 60                     ; syscall number: exit
    xor rdi, rdi                    ; exit status 0
    syscall
