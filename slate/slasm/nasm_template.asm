; SLASM_VERSION #SLASM_VERSION#
; TARGET #TARGET#

[BITS 64]

extern _printf

global _main

    section .text
    default rel

_main:
    ; create stack frame
    push rbp
    mov rbp, rsp

    ; call entry function
    call #ENTRY_FUNC_NAME#

    ; delete stack frame
    mov rsp, rbp
    pop rbp

    ; return (note that rax already contains the exit code from previous call instruction)
    ret

LINUX_x86_64_SYSCALL1:
    mov rax, [rsp + 8]  ; set syscall code
    mov rdi, [rsp + 16] ; set first argument
    syscall             ; perform syscall
    ret                 ; return

C_FUNC_3:
    push rbp                ; store old base pointer
    mov rbp, rsp            ; set new base pointer
    mov rsi, [rbp + 40]     ; set third argument
    mov rdi, [rbp + 32]     ; set second argument
    mov rax, [rbp + 24]     ; set first argument
    and  rsp, -16           ; align stack to 16-byte boundary
    call [rbp + 16]         ; perform C function call        
    mov rsp, rbp            ; clean up stack
    pop rbp                 ; restore old base pointer
    ret                     ; return

DEBUG_PRINT_I64:
    ; arg4 (number)
    mov rax, [rsp + 8]
    push rax

    ; arg3 (format)
    lea rax, [.fmt] 
    push rax
    
    ; arg2 (number of floating-point arguments)
    push 0

    ; arg1 (function address)
    lea rax, [_printf wrt ..gotpcrel]   ; obtain pointer to function address
    push QWORD [rax]                    ; deference pointer

    ; perform call
    call C_FUNC_3

    ; removed aruments
    add rsp, 32

    ; return
    ret

    ; LOCAL READONLY VARIABLES
    .fmt: db "%lli", 0x0A, 0

#SLASM_FUNCS#