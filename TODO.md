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
- Add ALLOCATE {amt} instruction that reserves [amt] bytes on the stack and pushes the pointer to its start on the stack
- Slasm functions must have a prologue and epilogue bc LOAD_LOCAL and LOAD_PARAM rely on rbp; Also wanna have it so that functions can return multiple values by just placing them on the stack
- Remove globals
  - Only use data
    - LOAD_DATA_ADDR {name}
    - LOAD_DATA {name}, {offset}
    - STORE_DATA {name}, {offset}
  - loading a global is LOAD_DATA {name}, {offset}
- The program class should have an is_valid to make sure functions are sound and the instructions within them are sound
- Rewrite DEBUG_PRINT_I64 as code rather than being in the template
- implement json loader
- create tests for each instruction
  - basically loading them from json
  - run through nasm emitter and compile (check for correct output; might wanna added _print)
  - run through llvm emitter and compile (check for correct output; might wanna added _print)
