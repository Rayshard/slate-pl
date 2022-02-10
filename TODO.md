# Slate
- Change most isinstance to type() equality
- Revert Location to Position in pylpc
- Change all `assert False, "Not Implemented"` to `raise NotImplementedError()"`

# Example Slate Programs
- Game of Life

# Slasm
- remove num_params and returns_value from CALL instruction and add that info to global/func ctx
- implement json loader
- create tests for each instruction
  - basically loading them from json
  - run through nasm emitter and compile (check for correct output; might wanna added _print)
  - run through llvm emitter and compile (check for correct output; might wanna added _print)