; ----------------------------------------------------------------------------------------
; Writes "Hello, World" to the console using only system calls. Runs on 64-bit macOS only.
; To assemble and run:
;
;     nasm -fmacho64 hello.asm && ld hello.o && ./a.out
; ----------------------------------------------------------------------------------------
BITS 64
        global    _main
        section   .text
_main:    
        mov       rax, 0x02000001         ; system call for exit
        push word 0x0000
        push word 0x0000
        push word 0x0000
        push word 0x000F

        mov eax, 0x00000000
        push dword eax
        mov ax, 0x00000000
        push word ax
        mov al, 0x00000000
        push byte al
        pop rdi
        syscall                           ; invoke operating system to exit

          section   .data
message:  db        "Hello, World", 10      ; note the newline at the end