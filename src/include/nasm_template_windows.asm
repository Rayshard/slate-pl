extern printf

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

                                                ; Console Message, 64 bit. V1.03
NULL              EQU 0                         ; Constants
STD_OUTPUT_HANDLE EQU -11

extern GetStdHandle                             ; Import external symbols
extern WriteFile                                ; Windows API functions, not decorated
extern ExitProcess

global Start                                    ; Export symbols. The entry point

section .data                                   ; Initialized data segment
    Message        db "Hello, World!", 0Dh, 0Ah
    MessageLength  EQU $-Message                   ; Address of this line ($) - address of Message

section .bss                                    ; Uninitialized data segment
alignb 8
    StandardHandle resq 1
    Written        resq 1

section .text                                   ; Code segment

C_CALL_3_WITH_RET: C_CALL_3
C_CALL_3_NO_RET: C_CALL_3

Start:
    ; arg4 (number)
    mov rax, [rsp + 8]
    push rax

    ; arg3 (format)
    lea rax, [.fmt] 
    push rax
    
    ; arg2 (number of floating-point arguments)
    push 0

    ; arg1 (function address)
    lea rax, [rel printf]   ; obtain pointer to function address
    push QWORD [rax]                    ; deference pointer

    ; perform call
    call C_CALL_3_NO_RET

    ; remove aruments
    add rsp, 32

    ; return
    ret

    ; LOCAL READONLY VARIABLES
    .fmt: db "%lli", 0x0A, 0

    ;other
    sub   RSP, 8                                   ; Align the stack to a multiple of 16 bytes

    sub   RSP, 32                                  ; 32 bytes of shadow space
    mov   ECX, STD_OUTPUT_HANDLE
    call  GetStdHandle
    mov   qword [REL StandardHandle], RAX
    add   RSP, 32                                  ; Remove the 32 bytes

    sub   RSP, 32 + 8 + 8                          ; Shadow space + 5th parameter + align stack
                                                   ; to a multiple of 16 bytes
    mov   RCX, qword [REL StandardHandle]          ; 1st parameter
    lea   RDX, [REL Message]                       ; 2nd parameter
    mov   R8, MessageLength                        ; 3rd parameter
    lea   R9, [REL Written]                        ; 4th parameter
    mov   qword [RSP + 4 * 8], NULL                ; 5th parameter
    call  WriteFile                                ; Output can be redirect to a file using >
    add   RSP, 48                                  ; Remove the 48 bytes

    xor   ECX, ECX
    call  ExitProcess