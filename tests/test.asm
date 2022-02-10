; SLASM_VERSION 1.0
; TARGET x86-64-linux-nasm

[BITS 64]

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

global _main

    section .text
    default rel

_main:
    ; create stack frame
    push rbp
    mov rbp, rsp

    ; call entry function
    call SLASM_Main

    ; delete stack frame
    mov rsp, rbp
    pop rbp

    ; return (note that rax already contains the exit code from previous call instruction)
    ret

LINUX_x86_64_SYSCALL1_WITH_RET: LINUX_x86_64_SYSCALL1
LINUX_x86_64_SYSCALL1_NO_RET: LINUX_x86_64_SYSCALL1
C_CALL_3_WITH_RET: C_CALL_3
C_CALL_3_NO_RET: C_CALL_3

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

SLASM_Main:
  .entry:
    ; LOAD_CONST 0x000000000000007b
    mov rax, 0x000000000000007b
    push rax
    ; CALL
    call DEBUG_PRINT_I64
    add rsp, 8 ; remove arguments from stack
    ; LOAD_CONST 0x0000000000000040
    mov rax, 0x0000000000000040
    push rax
    ; RET
    pop rax
    ret