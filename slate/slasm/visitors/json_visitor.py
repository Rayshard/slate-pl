import json
from typing import Any, Callable, Dict
from slate.slasm.function import Function
from slate.slasm.instruction import *
from slate.slasm.program import Program
from slate.slasm.slasm import VERSION

def __emit_NOOP(instr: NOOP) -> Any:
    return {"opcode": instr.opcode.name}

def __emit_LOAD_CONST(instr: LOAD_CONST) -> Any:
    return {"opcode": instr.opcode.name, "value": instr.value.as_hex()}

def __emit_LOAD_FUNC_ADDR(instr: LOAD_FUNC_ADDR) -> Any:
    return {"opcode": instr.opcode.name, "func_name": instr.func_name}

def __emit_CALL(instr: CALL) -> Any:
    return {"opcode": instr.opcode.name, "target": instr.target}

def __emit_RET(instr: RET) -> Any:
    return {"opcode": instr.opcode.name}

__TRANSLATORS : Dict[Any, Callable[..., Any]] = {
    OpCode.NOOP: __emit_NOOP,
    OpCode.LOAD_CONST: __emit_LOAD_CONST,
    OpCode.CALL: __emit_CALL,
    OpCode.RET: __emit_RET,
}

def emit_Instruction(instr: Instruction) -> Any:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __TRANSLATORS[instr.opcode](instr)

def emit_Function(function: Function) -> Any:
    return {
        "name": function.name,
        "returns_value": function.returns_value,
        "entry": function.entry,
        "params": list(function.params),
        "locals": list(function.locals),
        "basic_blocks": {label:[emit_Instruction(instr) for instr in bb] for label, bb in function.basic_blocks}
    }

def emit_Program(program: Program) -> Any:
    return {
        "slasm_version": VERSION(),
        "target": program.target,
        "entry": program.entry,
        "globals": list(program.globals),
        "functions": {func.name:emit_Function(func) for func in program.functions}
    }

def load_Program(json_value: Any) -> Program:
    assert isinstance(json_value, dict)

    program = Program(json_value["target"])

    for item in json_value["globals"].values():
        pass

    for item in json_value["functions"].values():
        pass

    program.entry = json_value["entry"]

    return program

def to_string(json_value: Any) -> str:
    return json.dumps(json_value, indent=4)
