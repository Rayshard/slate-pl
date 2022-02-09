; SLASM_VERSION 1.0
; TARGET x86-64-linux-nasm

    global _main

    section .text
_main:
    call SLASM_Main
    ret ; note that rax alreeady contains the exit code from previous call instruction

LINUX_x86_64_SYSCALL1:
    mov rax, [rsp + 8]
    mov rdi, [rsp + 16]
    syscall
    ret

SLASM_Main:
  .entry:
    ; LOAD_CONST 0x0000000000000040
    mov rax, 0x0000000000000040
    push rax
    ; RET
    pop rax
    ret