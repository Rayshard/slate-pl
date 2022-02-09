; SLASM_VERSION #SLASM_VERSION#
; TARGET #TARGET#

    global _main

    section .text
_main:
    call #ENTRY_FUNC_NAME#
    ret ; note that rax alreeady contains the exit code from previous call instruction

LINUX_x86_64_SYSCALL1:
    mov rax, [rsp + 8]
    mov rdi, [rsp + 16]
    syscall
    ret

#SLASM_FUNCS#