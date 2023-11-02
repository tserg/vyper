from typing import Optional

from vyper import ast as vy_ast


def get_folded_value(node: vy_ast.VyperNode) -> Optional[vy_ast.VyperNode]:
    if isinstance(node, vy_ast.Constant):
        return node
    elif isinstance(node, vy_ast.List):
        values = [get_folded_value(e) for e in node.elements]
        if None not in values:
            return type(node).from_node(node, elts=values)
    elif isinstance(node, vy_ast.Index):
        return get_folded_value(node.value)

    return node._metadata.get("folded_value")
