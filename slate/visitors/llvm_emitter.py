from slate.slate_ast import ASTIntegerLiteral, ASTModule, ASTNode
from llvmlite import ir # type: ignore

TypeI64 = ir.IntType(64)

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral) -> ir.Value:
    return ir.Constant(TypeI64, node.get_value())

def __visit_ASTNode(node: ASTNode, builder: ir.IRBuilder) -> ir.Value:
    if isinstance(node, ASTIntegerLiteral):
        return __visit_ASTIntegerLiteral(node)

    raise NotImplementedError(type(node))

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