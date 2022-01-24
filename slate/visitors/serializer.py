from typing import Any, Callable, Dict, Optional
from slate.ast import ASTBinopExpr, ASTExpr, ASTIntegerLiteral, ASTModule, ASTNode, ASTVarDecl
import xml.etree.ElementTree as ET

def __visit_ASTIntegerLiteral(node: ASTIntegerLiteral) -> ET.Element:
    return ET.Element("IntergerLiteral", {"value": str(node.get_value())})

def __visit_ASTBinopExpr(node: ASTBinopExpr) -> ET.Element:
    element = ET.Element("BinopExpr", {"op": node.get_op().name})
    element.append(__visit_ASTNode(node.get_lhs()))
    element.append(__visit_ASTNode(node.get_rhs()))
    return element

def __visit_ASTVarDecl(node: ASTVarDecl) -> ET.Element:
    element = ET.Element("VarDecl", {"id": node.get_id(), "constraint": str(node.get_constraint())})
    element.append(__visit_ASTNode(node.get_expr()))
    return element

__VISITORS : Dict[Any, Callable[..., ET.Element]] = {
    ASTIntegerLiteral: __visit_ASTIntegerLiteral,
    ASTBinopExpr: __visit_ASTBinopExpr,
    ASTVarDecl: __visit_ASTVarDecl,
}

def __visit_ASTNode(node: ASTNode) -> ET.Element:
    serialization : Optional[ET.Element] = None
    
    if type(node) not in __VISITORS:
        raise NotImplementedError(type(node))

    serialization = __VISITORS[type(node)](node)
    
    if node.is_type_checked() and isinstance(node, ASTExpr):
        serialization.attrib["slate_type"] = str(node.get_slate_type())

    return serialization

def visit(module: ASTModule) -> ET.Element:
    element = ET.Element("Module", {"path": module.get_path()})
    
    for node in module.get_nodes():
        element.append(__visit_ASTNode(node))

    return element
