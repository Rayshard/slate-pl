from typing import Any, Dict, Optional, Union
from slate.slate_ast import ASTIntegerLiteral, ASTModule, ASTNode

Serialization = Dict[str, Any]

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral) -> Serialization:
    return {
        "__instance__": "IntergerLiteral",
        "value": node.get_value()
    }

def __visit_ASTNode(node: ASTNode) -> Serialization:
    serialization : Optional[Serialization] = None

    if isinstance(node, ASTIntegerLiteral):
        serialization = __visit_ASTIntegerLiteral(node)
    else:
        raise NotImplementedError(type(node))

    assert "__instance__" in serialization
    return serialization

def visit(module: ASTModule) -> Serialization:
    return {
        "path": module.get_path(),
        "nodes": [__visit_ASTNode(node) for node in module.get_nodes()]
    }
