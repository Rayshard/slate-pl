    global _main

    section .text
_main:
FUNC_Main:
    ; PUSH 0x000000000000007b
    MOV RAX, 0x000000000000007b
    PUSH RAX
    ; SYSCALL_LINUX 33554433, 1
    MOV RAX, 33554433
    POP RDI
    SYSCALL
    ; RET
    RET