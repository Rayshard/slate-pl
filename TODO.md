# Slate
- Change the type of ASTIntegerLiteral
  - There should be a general IntType that takes a arbitrary byte_size
  - It can then be truncated/casted as needed
- Change most isinstance to type() equality
- Revert Location to Position in pylpc
- Change all `assert False, "Not Implemented"` to `raise NotImplementedError()"`

# Example Slate Programs
- Game of Life

# Slasm
- Implement globals
  - They can be readonly or writeable
  - The program class should have an is_valid to make sure functions are sound and the instructions within them are sound
    - e.g. you can't call a store_global on a readonly global
- Rewrite DEBUG_PRINT_I64 as code rather than being in the template
- implement json loader
- create tests for each instruction
  - basically loading them from json
  - run through nasm emitter and compile (check for correct output; might wanna added _print)
  - run through llvm emitter and compile (check for correct output; might wanna added _print)