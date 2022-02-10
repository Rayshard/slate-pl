; SLASM_VERSION 1.0
; TARGET x86-64-linux-nasm

[BITS 64]

    extern _printf

fmt_PRINT_I64: db "%lli", 0x0a, 0

    global _main

    section .text
    default rel

_main:
    push rbp
    mov rbp, rsp
    call SLASM_Main
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
    push rbp
    mov rbp, rsp
    
    ; number
    mov rax, [rbp + 16]
    push rax

    ; format
    lea rax, [rel fmt_PRINT_I64] 
    push rax
    
    ; number of variadic arguments
    push 0

    ; function address
    lea rax, [rel _printf wrt ..gotpcrel]
    push QWORD [rax]

    call C_FUNC_3

    mov rsp, rbp ; clean stack
    pop rbp
    ret
    ; push rbp
    ; mov rbp, rsp
    ; lea rdi, [rel fmt_PRINT_I64]    ; set first argument to format
    ; mov rsi, [rbp + 16]             ; set second argument to input number
    ; xor rax, rax                    ; since _printf is variadic, rax refers to the amount of SSE registers used (none in this case)
    ; push rsp                        ; save stack pointer
    ; and  rsp, -16                   ; align stack to 16-byte boundary
    ; call _printf                    
    ; pop rsp                         ; restore stack pointer
    ; pop rbp
    ; ret

SLASM_Main:
  .entry:
    ; LOAD_CONST 0x000000000000007b
    mov rax, 0x000000000000007b
    push rax
    ; NATIVE CALL
    call print_i64
    add rsp, 8 ; remove arguments from stack
    ; LOAD_CONST 0x0000000000000040
    mov rax, 0x0000000000000040
    push rax
    ; RET
    pop rax
    ret