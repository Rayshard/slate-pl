from typing import Any, Callable, Dict, List
from slate.ast import ASTBinopExpr, ASTExport, ASTExpr, ASTIntegerLiteral, ASTModule, ASTNode, ASTVarDecl, Binop
from slate.typesystem import EnvironmentError, ModuleContext, SlateFunction, SlateType
from slate.utilities import Location

class TCError(Exception):
    def __init__(self, loc: Location, msg: str) -> None:
        super().__init__(f"{loc} [Error] {msg}")

    @staticmethod
    def UnknownOverload(func_name: str, func_signatures: List[SlateFunction], attempted_params: List[SlateType], loc: Location) -> 'TCError':
        msg = f"'{func_name}' has no overload with parameters ({str.join(',', [str(p) for p in attempted_params])}). Avaiable signatures are:"
        
        for sig in func_signatures:
            msg += f"\n\t{func_name}: {sig}"

        return TCError(loc, msg)

__BINOP_FUNC_NAMES = {
    Binop.ADD: "operator+",
    Binop.SUB: "operator-",
    Binop.MULTIPLY: "operator*",
    Binop.DIVIDE: "operator/",
}

assert all([binop in __BINOP_FUNC_NAMES for binop in Binop])

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral, ctx: ModuleContext) -> ASTNode:
    return node

def __visit_ASTExport(node: ASTExport, ctx: ModuleContext) -> ASTNode:
    export = __visit_ASTNode(node.get_node(), ctx)

    if isinstance(export, ASTVarDecl):
        ctx.add_export(export.get_id(), ctx.get_cur_env().get_definition(export.get_id()))
    else:
        assert False, "Not Implemented"

    return export

def __visit_ASTBinopExpr(node: ASTBinopExpr, ctx: ModuleContext) -> ASTNode:
    lhs, rhs = __visit_ASTNode(node.get_lhs(), ctx), __visit_ASTNode(node.get_rhs(), ctx)
    assert isinstance(lhs, ASTExpr) and isinstance(rhs, ASTExpr)

    location = Location(ctx.get_module_path(), node.get_position())

    try:
        operator_def = ctx.get_cur_env().get_definition(__BINOP_FUNC_NAMES[node.get_op()])
        assert isinstance(operator_def.slate_type, SlateFunction)

        expected_params = [lhs.get_slate_type(), rhs.get_slate_type()]
        if not operator_def.slate_type.same_params(expected_params):
            raise TCError.UnknownOverload(operator_def.name, [operator_def.slate_type], expected_params, location)

        return ASTBinopExpr(lhs, node.get_op(), rhs, node.get_position(), operator_def.slate_type.get_ret())
    except EnvironmentError as e:
        raise TCError(location, str(e))

__VISITORS : Dict[Any, Callable[..., ASTNode]] = {
    ASTIntegerLiteral: __visit_ASTIntegerLiteral,
    ASTBinopExpr: __visit_ASTBinopExpr,
    ASTExport: __visit_ASTExport
}

def __visit_ASTNode(node: ASTNode, ctx: ModuleContext) -> ASTNode:   
    if type(node) not in __VISITORS:
        raise NotImplementedError(type(node))

    return __VISITORS[type(node)](node, ctx)

def visit(module: ASTModule) -> ASTModule:
    ctx = ModuleContext(module.get_path())
    nodes = [__visit_ASTNode(node, ctx) for node in module.get_nodes()]

    return ASTModule(module.get_path(), nodes, ctx)