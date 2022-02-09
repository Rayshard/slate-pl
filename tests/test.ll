; ModuleID = ""
target triple = "unknown-unknown-unknown"
target datalayout = ""

define void @"LINUX_x86_64_SYSCALL1"(i64 %".1", i64 %".2") 
{
.4:
  call void asm sideeffect "movq $0, %rax
movq $1, %rdi
syscall", "r,r"
(i64 %".1", i64 %".2")
  ret void
}

define i64 @"SLASM_Main"() 
{
entry:
  ret i64 64
}

define i32 @"main"() 
{
.2:
  %".3" = call i64 @"SLASM_Main"()
  %".4" = trunc i64 %".3" to i32
  ret i32 %".4"
}
