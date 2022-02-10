# Slate
- Change most isinstance to type() equality
- Revert Location to Position in pylpc
- Change all `assert False, "Not Implemented"` to `raise NotImplementedError()"`

# Example Slate Programs
- Game of Life

# Slasm
- remove num_params and returns_value from CALL instruction and add that info to global/func ctx
- Is nasm, you have to save rdi, rsi and possible others because they are caller saved
- Rewrite DEBUG_PRINT_I64 as code rather than being in the template
- implement json loader
- create tests for each instruction
  - basically loading them from json
  - run through nasm emitter and compile (check for correct output; might wanna added _print)
  - run through llvm emitter and compile (check for correct output; might wanna added _print)