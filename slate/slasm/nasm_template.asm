; SLASM_VERSION #SLASM_VERSION#
; TARGET #TARGET#

[BITS 64]

    extern _printf

fmt_PRINT_I64: db "%lli", 0x0a, 0

    global _main

    section .text
    default rel

_main:
    push rbp
    mov rbp, rsp
    call #ENTRY_FUNC_NAME#
    pop rbp
    ret ; note that rax alreeady contains the exit code from previous call instruction

LINUX_x86_64_SYSCALL1:
    mov rax, [rsp + 8]
    mov rdi, [rsp + 16]
    syscall
    ret

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

print_i64:
    ; create stack frame
    push rbp
    mov rbp, rsp
    
    ; push number
    mov rax, [rbp + 16]
    push rax

    ; push format
    lea rax, [rel fmt_PRINT_I64] 
    push rax
    
    ; push number of floating-point arguments
    push 0

    ; push function address
    lea rax, [rel _printf wrt ..gotpcrel]   ; obtain pointer to function address
    push QWORD [rax]                        ; deference pointer

    ; perform call
    call C_FUNC_3

    ; delete stack frame
    mov rsp, rbp
    pop rbp
    ret

#SLASM_FUNCS#