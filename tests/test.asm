    global _main

    section .text
_main:
FUNC_Main:
    ; LOAD_CONST 0x000000000000007b
    MOV RAX, 0x000000000000007b
    PUSH RAX
  .Label1:
  .Label2:
    ; LOAD_LABEL Label1
    LEA RAX, [REL .Label1]
    PUSH RAX
    ; SYSCALL_LINUX 33554433, 1
    MOV RAX, 0x0000000002000001
    POP RDI
    SYSCALL
  .LabelRet:
    ; RET
    RET