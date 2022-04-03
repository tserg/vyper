from vyper.ast import nodes as vy_ast
from vyper.exceptions import CompilerPanic


def postprocess_ast(vyper_module: vy_ast.Module) -> None:
    """
    Perform post-processing operations on an annotated Vyper AST.

    This pass modifies the AST based on pre-parser rules that are unique to Vyper
    (and as a result may not be valid Python syntax).

    Specific operations are:
    1.  Unmangling of tuple declarations

    Arguments
    ---------
    vyper_module : Module
        Top-level Vyper AST node that has been parsed from Python AST but before
        type-checking and annotation.
    """
    unmangle_tuple_declarations(vyper_module)


def unmangle_tuple_declarations(vyper_module: vy_ast.Module) -> None:
    """
    Replace single name nodes that are mangled tuple declarations with a Tuple node and
    the respective children name nodes.

    This information needs to be in the AST before further annotation, validation and
    type-checking.

    Arguments
    ---------
    vyper_module : Module
        Top-level Vyper AST node.
    """
    for node in vyper_module.get_descendants(vy_ast.AnnAssign):
        targets = node.target.id.split("__")

        if len(targets) < 2:
            continue

        if not isinstance(node.annotation, vy_ast.Tuple):
            raise CompilerPanic("Tuple declaration found without defined types")

        # TODO: Function calls need to be handled
        if len(targets) != len(node.annotation.elements):
            raise CompilerPanic("Tuple declaration has incorrect number of values")

        # Unmangle the tuple identifier and construct new Vyper Name nodes for each
        # identifier
        res = []

        node_id_count = len(vyper_module.get_descendants())

        for id in targets:
            new_id = vy_ast.Name().from_node(node.target, id=id, node_id=node_id_count)
            node_id_count += 1
            res.append(new_id)

        # Create Vyper Tuple node with the node id of the original mangled identifier
        tuple_node = vy_ast.Tuple().from_node(
            node.target, elements=res, node_id=node.target.node_id
        )

        node.tuple_target = zip(targets, node.annotation.elements, node.value.elements)

        vyper_module.replace_in_tree(node.target, tuple_node)
