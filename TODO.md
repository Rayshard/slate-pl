# Slate
- Change most isinstance to type() equality
- Revert Location to Position in pylpc
- Change all `assert False, "Not Implemented"` to `raise NotImplementedError()"`

# Slasm
- have translate_nasm function take in `template` rather than headers
- Change asserts to raise NotImplementedError()
- change instructions in slasm to classes

