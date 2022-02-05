%macro LINUX_x86_64_SYSCALL1 1
    MOV RAX, %1
    POP RDI
    SYSCALL
%endmacro