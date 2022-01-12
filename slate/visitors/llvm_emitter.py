from typing import Any, Callable, Dict
from slate.slate_ast import ASTBinopExpr, ASTIntegerLiteral, ASTModule, ASTNode, Binop
from llvmlite import ir # type: ignore

TypeI64 = ir.IntType(64)

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral, _: ir.IRBuilder) -> ir.Value:
    return ir.Constant(TypeI64, node.get_value())

def __visit_ASTBinopExpr(node: ASTBinopExpr, builder: ir.IRBuilder) -> ir.Value:
    op = node.get_op()
    lhs, rhs = __visit_ASTNode(node.get_lhs(), builder), __visit_ASTNode(node.get_rhs(), builder)
    
    if op == Binop.ADD:
        return builder.add(lhs, rhs)
    elif op == Binop.SUB:
        return builder.sub(lhs, rhs)
    elif op == Binop.MULTIPLY:
        return builder.mul(lhs, rhs)
    elif op == Binop.DIVIDE:
        return builder.sdiv(lhs, rhs)

    raise NotImplementedError(op)

__VISITORS : Dict[Any, Callable[..., ir.Value]] = {
    ASTIntegerLiteral: __visit_ASTIntegerLiteral,
    ASTBinopExpr: __visit_ASTBinopExpr
}

def __visit_ASTNode(node: ASTNode, builder: ir.IRBuilder) -> ir.Value:
    if type(node) not in __VISITORS:
        raise NotImplementedError(type(node))

    return __VISITORS[type(node)](node, builder)

def visit(module: ASTModule, ir_module: ir.Module) -> ir.Module:
    entry_func_type = ir.FunctionType(TypeI64, ())
    entry_func = ir.Function(ir_module, entry_func_type, module.get_path() + "#entry")
    start_block = entry_func.append_basic_block("start")
    builder = ir.IRBuilder(start_block)

    last_value = ir.Constant(TypeI64, 0)

    for node in module.get_nodes():
        last_value = __visit_ASTNode(node, builder)

    builder.ret(last_value)
    return ir_module