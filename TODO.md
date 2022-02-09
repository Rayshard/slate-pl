# Slate
- Change most isinstance to type() equality
- Revert Location to Position in pylpc
- Change all `assert False, "Not Implemented"` to `raise NotImplementedError()"`

# Slasm
- rename LOAD_FUNC_ADDR.name to LOAD_FUNC_ADDR.func_name
- rename functions under emitters to emit rather than translate
- have translate_nasm function take in `template` rather than headers
- Change asserts to raise NotImplementedError()
- change instructions in slasm to classes

