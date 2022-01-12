from typing import Any, Callable, Dict, Optional, Type, Union
from slate.ast import ASTBinopExpr, ASTIntegerLiteral, ASTModule, ASTNode

Serialization = Dict[str, Any]

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral) -> Serialization:
    return {
        "__instance__": "IntergerLiteral",
        "value": node.get_value()
    }

def __visit_ASTBinopExpr(node: ASTBinopExpr) -> Serialization:
    return {
        "__instance__": "BinopExpr",
        "op": node.get_op().name,
        "lhs": __visit_ASTNode(node.get_lhs()),
        "rhs": __visit_ASTNode(node.get_rhs())
    }

__VISITORS : Dict[Any, Callable[..., Serialization]] = {
    ASTIntegerLiteral: __visit_ASTIntegerLiteral,
    ASTBinopExpr: __visit_ASTBinopExpr
}

def __visit_ASTNode(node: ASTNode) -> Serialization:
    serialization : Optional[Serialization] = None
    
    if type(node) not in __VISITORS:
        raise NotImplementedError(type(node))

    serialization = __VISITORS[type(node)](node)
    assert "__instance__" in serialization
    
    return serialization

def visit(module: ASTModule) -> Serialization:
    return {
        "path": module.get_path(),
        "nodes": [__visit_ASTNode(node) for node in module.get_nodes()]
    }
