import json
from typing import Any, Callable, Dict
from slate.slasm.function import Function
from slate.slasm.instruction import ADD, DIV, LOAD_CONST, LOAD_FUNC_ADDR, LOAD_GLOBAL, LOAD_LOCAL, LOAD_MEM, LOAD_PARAM, MOD, MUL, NATIVE_CALL, NOOP, POP, RET, STORE_GLOBAL, STORE_LOCAL, STORE_MEM, STORE_PARAM, SUB, Instruction, OpCode
from slate.slasm.program import Program
from slate.slasm.slasm import VERSION

def __emit_NOOP(instr: NOOP) -> Any:
    return {"opcode": instr.opcode.name}

def __emit_LOAD_CONST(instr: LOAD_CONST) -> Any:
    return {"opcode": instr.opcode.name, "value": instr.value.as_hex()}

def __emit_NATIVE_CALL(instr: NATIVE_CALL) -> Any:
    return {"opcode": instr.opcode.name, "target": instr.target, "num_params": instr.num_params, "returns_value": instr.returns_value}

def __emit_RET(instr: RET) -> Any:
    return {"opcode": instr.opcode.name}

__TRANSLATORS : Dict[Any, Callable[..., Any]] = {
    OpCode.NOOP: __emit_NOOP,
    OpCode.LOAD_CONST: __emit_LOAD_CONST,
    OpCode.NATIVE_CALL: __emit_NATIVE_CALL,
    OpCode.RET: __emit_RET,
}

def emit_Instruction(instr: Instruction) -> Any:
    if instr.opcode not in __TRANSLATORS:
        raise NotImplementedError(instr.opcode)

    return __TRANSLATORS[instr.opcode](instr)

def emit_Function(function: Function) -> Any:
    return {
        "name": function.name,
        "params": function.num_params,
        "locals": function.num_locals,
        "returns_value": function.returns_value,
        "entry": function.entry,
        "basic_blocks": {label:[emit_Instruction(instr) for instr in bb] for label, bb in function.basic_blocks}
    }

def emit_Program(program: Program) -> Any:
    return {
        "slasm_version": VERSION(),
        "target": program.target,
        "code": {
            "entry": program.entry,
            "functions": {func.name:emit_Function(func) for func in program.functions}
        }
    }

def load_Program(json_value: Any) -> Program:
    assert isinstance(json_value, dict)

    program = Program(json_value["target"])

    for item in program["code"]["functions"].values():
        pass

    program.entry = json_value["code"]["entry"]

    return program

def to_string(json_value: Any) -> str:
    return json.dumps(json_value, indent=4)
