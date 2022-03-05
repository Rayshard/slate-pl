extern _printf

%macro LINUX_x86_64_SYSCALL1 0
    mov rax, [rsp + 8]  ; set syscall code
    mov rdi, [rsp + 16] ; set first argument
    syscall             ; perform syscall
    ret                 ; return
%endmacro

%macro C_CALL_3 0
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
%endmacro

    section .text

    default rel
    global _main

LINUX_x86_64_SYSCALL1_WITH_RET: LINUX_x86_64_SYSCALL1
LINUX_x86_64_SYSCALL1_NO_RET: LINUX_x86_64_SYSCALL1
C_CALL_3_WITH_RET: C_CALL_3
C_CALL_3_NO_RET: C_CALL_3

_main:
    ; create stack frame
    push rbp
    mov rbp, rsp

    ; call entry function
    call Main

    ; delete stack frame
    mov rsp, rbp
    pop rbp

    ; return (note that rax already contains the exit code from previous call instruction)
    ret

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
    call C_CALL_3_NO_RET

    ; remove aruments
    add rsp, 32

    ; return
    ret

    ; LOCAL READONLY VARIABLES
    .fmt: db "%lli", 0x0A, 0
; ==================== END OF HEADER ====================

; GENERATED FROM SLASM VERSION 1.0.0

    section .data
my_string: db 72, 101, 108, 108, 111, 44, 32, 87, 111, 114, 108, 100, 33, 0

    section .text
Main:
    .entry:
        ; push 0F:0E:0D:0C:0B:0A:09:08:07:06:05:04:03:02
        mov rax, 0x0F0E0D0C0B0A0908
        push rax
        mov rax, 0x0706050403020000
        push rax
        add rsp, 2

        ; call Main
        call Main
        add rsp, 24 ; leave only the return buffer on the stack

