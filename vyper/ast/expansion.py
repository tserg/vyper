import copy

from vyper import ast as vy_ast
from vyper.exceptions import CompilerPanic
from vyper.semantics.types.function import ContractFunctionT


def generate_public_variable_getters(vyper_module: vy_ast.Module) -> None:
    """
    Create getter functions for public variables.

    Arguments
    ---------
    vyper_module : Module
        Top-level Vyper AST node.
    """

    for node in vyper_module.get_children(vy_ast.VariableDecl, {"is_public": True}):
        typ = node._metadata["type"]
        func_type = node._metadata["func_type"]
        input_types, return_type = typ.getter_signature
        input_nodes = []

        # use the annotation node to build the input args and return type
        annotation = copy.copy(node.annotation)

        return_stmt: vy_ast.VyperNode
        # constants just return a value
        if node.is_constant:
            return_stmt = node.value
        elif node.is_immutable:
            return_stmt = vy_ast.Name(id=func_type.name)
        else:
            # the base return statement is an `Attribute` node, e.g. `self.<var_name>`
            # for each input type we wrap it in a `Subscript` to access a specific member
            return_stmt = vy_ast.Attribute(value=vy_ast.Name(id="self"), attr=func_type.name)
        return_stmt._metadata["type"] = typ

        for i, type_ in enumerate(input_types):
            if not isinstance(annotation, vy_ast.Subscript):
                # if we get here something has failed in type checking
                raise CompilerPanic("Mismatch between node and input type while building getter")
            if annotation.value.get("id") == "HashMap":  # type: ignore
                # for a HashMap, split the key/value types and use the key type as the next arg
                arg, annotation = annotation.slice.value.elements  # type: ignore
            elif annotation.value.get("id") == "DynArray":
                arg = vy_ast.Name(id=type_._id)
                annotation = annotation.slice.value.elements[0]  # type: ignore
            else:
                # for other types, build an input arg node from the expected type
                # and remove the outer `Subscript` from the annotation
                arg = vy_ast.Name(id=type_._id)
                annotation = annotation.value
            input_nodes.append(vy_ast.arg(arg=f"arg{i}", annotation=arg))

            # wrap the return statement in a `Subscript`
            return_stmt = vy_ast.Subscript(
                value=return_stmt, slice=vy_ast.Index(value=vy_ast.Name(id=f"arg{i}"))
            )

        # after iterating the input types, the remaining annotation node is our return type
        return_node = copy.copy(annotation)

        # join everything together as a new `FunctionDef` node, annotate it
        # with the type, and append it to the existing `Module` node
        expanded = vy_ast.FunctionDef.from_node(
            node.annotation,
            name=func_type.name,
            args=vy_ast.arguments(args=input_nodes, defaults=[]),
            body=[vy_ast.Return(value=return_stmt)],
            decorator_list=[vy_ast.Name(id="external"), vy_ast.Name(id="view")],
            returns=return_node,
        )

        with vyper_module.namespace():
            func_type = ContractFunctionT.from_FunctionDef(expanded)

        expanded._metadata["type"] = func_type
        return_node.set_parent(expanded)
        vyper_module.add_to_body(expanded)


def remove_unused_statements(vyper_module: vy_ast.Module) -> None:
    """
    Remove statement nodes that are unused after type checking.

    Once type checking is complete, we can remove now-meaningless statements to
    simplify the AST prior to IR generation.

    Arguments
    ---------
    vyper_module : Module
        Top-level Vyper AST node.
    """
    # `implements: interface` statements - validated during type checking
    for node in vyper_module.get_children(vy_ast.ImplementsDecl):
        vyper_module.remove_from_body(node)
