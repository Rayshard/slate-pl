; SLASM_VERSION 1.0
; TARGET x86-64-linux

%macro LINUX_x86_64_SYSCALL1 1
    MOV RAX, %1
    POP RDI
    SYSCALL
%endmacro

    global _main

    section .text
_main:
FUNC_Main:
    ; LOAD_CONST 0x000000000000007b
    MOV RAX, 0x000000000000007b
    PUSH RAX
    ; NATIVE ASSEMBLY
    LINUX_x86_64_SYSCALL1 0x2000001
    ; RET
    RET