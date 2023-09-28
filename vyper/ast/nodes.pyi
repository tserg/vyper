import ast as python_ast
from typing import Any, Callable, Optional, Sequence, Type, Union

from .natspec import parse_natspec as parse_natspec
from .utils import ast_to_dict as ast_to_dict
from .utils import parse_to_ast as parse_to_ast
from .utils import parse_to_ast_with_settings as parse_to_ast_with_settings

NODE_BASE_ATTRIBUTES: Any
NODE_SRC_ATTRIBUTES: Any
DICT_AST_SKIPLIST: Any

def get_node(
    ast_struct: Union[dict, python_ast.AST], parent: Optional[VyperNode] = ...
) -> VyperNode: ...
def compare_nodes(left_node: VyperNode, right_node: VyperNode) -> bool: ...

class VyperNode:
    full_source_code: str = ...
    node_source_code: str = ...
    _metadata: dict = ...
    def __init__(self, parent: Optional[VyperNode] = ..., **kwargs: Any) -> None: ...
    def __hash__(self) -> Any: ...
    def __eq__(self, other: Any) -> Any: ...
    @property
    def description(self): ...
    @classmethod
    def get_fields(cls: Any) -> set: ...
    def evaluate(self) -> VyperNode: ...
    @classmethod
    def from_node(cls, node: VyperNode, **kwargs: Any) -> Any: ...
    def to_dict(self) -> dict: ...
    def get_children(
        self,
        node_type: Union[Type[VyperNode], Sequence[Type[VyperNode]], None] = ...,
        filters: Optional[dict] = ...,
        reverse: bool = ...,
    ) -> Sequence: ...
    def get_descendants(
        self,
        node_type: Union[Type[VyperNode], Sequence[Type[VyperNode]], None] = ...,
        filters: Optional[dict] = ...,
        include_self: bool = ...,
        reverse: bool = ...,
    ) -> Sequence: ...
    def get_ancestor(
        self, node_type: Union[Type[VyperNode], Sequence[Type[VyperNode]], None] = ...
    ) -> VyperNode: ...
    def get(self, field_str: str) -> Any: ...

class TopLevel(VyperNode):
    doc_string: Str = ...
    body: list = ...
    name: str = ...
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __contains__(self, obj: Any) -> bool: ...

class Module(TopLevel):
    def replace_in_tree(self, old_node: VyperNode, new_node: VyperNode) -> None: ...
    def add_to_body(self, node: VyperNode) -> None: ...
    def remove_from_body(self, node: VyperNode) -> None: ...
    def namespace(self) -> Any: ...  # context manager

class FunctionDef(TopLevel):
    args: arguments = ...
    decorator_list: list = ...
    returns: VyperNode = ...

class arguments(VyperNode):
    args: list = ...
    defaults: list = ...

class arg(VyperNode): ...
class Return(VyperNode): ...

class Log(VyperNode):
    value: VyperNode = ...

class EnumDef(VyperNode):
    body: list = ...
    name: str = ...

class EventDef(VyperNode):
    body: list = ...
    name: str = ...

class InterfaceDef(VyperNode):
    body: list = ...
    name: str = ...

class StructDef(VyperNode):
    body: list = ...
    name: str = ...

class ExprNode(VyperNode): ...

class Constant(VyperNode):
    value: Any = ...

class Num(Constant):
    @property
    def n(self): ...

class Int(Num):
    value: int = ...

class Decimal(Num): ...

class Hex(Num):
    @property
    def n_bytes(self): ...

class Str(Constant):
    @property
    def s(self): ...

class Bytes(Constant):
    @property
    def s(self): ...

class List(VyperNode):
    elements: list = ...

class Tuple(VyperNode):
    elements: list = ...

class Dict(VyperNode):
    keys: list = ...
    values: list = ...

class NameConstant(Constant): ...

class Name(VyperNode):
    id: str = ...
    _type: str = ...

class Expr(VyperNode):
    value: VyperNode = ...

class UnaryOp(ExprNode):
    op: Operator = ...
    operand: VyperNode = ...

class Operator(VyperNode):
    @property
    def _op(self) -> Callable: ...

class USub(Operator):
    pass

class Not(Operator):
    pass

class BinOp(ExprNode):
    left: VyperNode = ...
    op: Operator = ...
    right: VyperNode = ...

class Add(Operator):
    pass

class Sub(Operator):
    pass

class Mult(Operator):
    pass

class Div(Operator):
    pass

class Mod(Operator):
    pass

class Pow(Operator):
    pass

class LShift(Operator):
    pass

class RShift(Operator):
    pass

class BitAnd(Operator):
    pass

class BitOr(Operator):
    pass

class BitXor(Operator):
    pass

class BoolOp(ExprNode):
    op: Operator = ...
    values: list[VyperNode] = ...

class And(Operator): ...
class Or(Operator): ...

class Compare(ExprNode):
    op: Operator = ...
    left: VyperNode = ...
    right: VyperNode = ...

class Eq(Operator):
    pass

class NotEq(Operator):
    pass

class Lt(Operator):
    pass

class LtE(Operator):
    pass

class Gt(Operator):
    pass

class GtE(Operator):
    pass

class In(Operator):
    pass

class NotIn(Operator):
    pass

class Call(ExprNode):
    args: list = ...
    keywords: list = ...
    func: Name = ...

class keyword(VyperNode): ...

class Attribute(VyperNode):
    attr: str = ...
    value: VyperNode = ...

class Subscript(VyperNode):
    slice: Index = ...
    value: VyperNode = ...

class Index(VyperNode):
    value: Constant = ...

class Assign(VyperNode): ...

class AnnAssign(VyperNode):
    target: Name = ...
    value: VyperNode = ...
    annotation: VyperNode = ...

class VariableDecl(VyperNode):
    target: Name = ...
    value: VyperNode = ...
    annotation: VyperNode = ...
    is_constant: bool = ...
    is_public: bool = ...
    is_immutable: bool = ...

class AugAssign(VyperNode):
    op: Operator = ...
    target: VyperNode = ...
    value: VyperNode = ...

class Raise(VyperNode): ...
class Assert(VyperNode): ...
class Pass(VyperNode): ...

class Import(VyperNode):
    alias: str = ...
    name: str = ...

class ImportFrom(VyperNode):
    alias: str = ...
    level: int = ...
    module: str = ...
    name: str = ...

class ImplementsDecl(VyperNode):
    target: Name = ...
    annotation: Name = ...

class If(VyperNode):
    body: list = ...
    orelse: list = ...

class IfExp(ExprNode):
    test: ExprNode = ...
    body: ExprNode = ...
    orelse: ExprNode = ...

class For(VyperNode): ...
class Break(VyperNode): ...
class Continue(VyperNode): ...
