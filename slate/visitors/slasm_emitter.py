from typing import Any, Callable, Dict, List, Optional
from slate.ast import ASTBinopExpr, ASTIntegerLiteral, ASTModule, ASTNode, Binop
from slate.slasm.function import BasicBlock, Function
from slate.slasm import instruction
from slate.slasm.program import Program
from slate.slasm.slasm import DataType, Word
from slate import typesystem
from slate.utilities import i64

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral, basic_block: BasicBlock, function: Function) -> Optional[BasicBlock]:
    if node.get_slate_type().same_as(typesystem.I64()):
        basic_block.append_instr(instruction.LOAD_CONST(Word.FromI64(i64(node.get_value()))))
    else:
        raise NotImplementedError(node.get_slate_type())

    return basic_block

def __visit_ASTBinopExpr(node: ASTBinopExpr, basic_block: BasicBlock, function: Function) -> Optional[BasicBlock]:
    bb = __visit_ASTNode(node.get_lhs(), basic_block, function)
    assert bb is not None

    bb = __visit_ASTNode(node.get_rhs(), bb, function)
    assert bb is not None
    
    op = node.get_op()

    if not node.get_lhs().get_slate_type().same_as(typesystem.I64()) or not node.get_rhs().get_slate_type().same_as(typesystem.I64()) or not node.get_slate_type().same_as(typesystem.I64()):
        raise NotImplementedError()

    if op == Binop.ADD:
        bb.append_instr(instruction.ADD(DataType.I64))
    elif op == Binop.SUB:
        bb.append_instr(instruction.SUB(DataType.I64))
    elif op == Binop.MULTIPLY:
        bb.append_instr(instruction.MUL(DataType.I64))
    elif op == Binop.DIVIDE:
        bb.append_instr(instruction.DIV(DataType.I64))
    else:
        raise NotImplementedError(op)

    return bb

__VISITORS : Dict[Any, Callable[..., Optional[BasicBlock]]] = {
    ASTIntegerLiteral: __visit_ASTIntegerLiteral,
    ASTBinopExpr: __visit_ASTBinopExpr
}

def __visit_ASTNode(node: ASTNode, basic_block: BasicBlock, function: Function) -> Optional[BasicBlock]:
    if type(node) not in __VISITORS:
        raise NotImplementedError(type(node))

    return __VISITORS[type(node)](node, basic_block, function)

def visit(modules: List[ASTModule], target: str) -> Program:
    program = Program(target)
    function = Function("Main", 0, 0, True)

    basic_block = BasicBlock()
    
    for module in modules:
        for node in module.get_nodes():
            bb = __visit_ASTNode(node, basic_block, function)

            if bb is None:
                raise NotImplementedError()

            basic_block = bb

    basic_block.append_instr(instruction.CALL("DEBUG_PRINT_I64"))
    basic_block.append_instr(instruction.LOAD_CONST(Word.FromI64(i64(35))))
    basic_block.append_instr(instruction.RET())

    function.add_basic_block("entry", basic_block)
    function.entry = "entry"

    program.add_function(function)
    program.entry = function.name

    return program