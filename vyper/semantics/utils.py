from collections import OrderedDict


class MemberInfoDict(OrderedDict):
    """
    OrderedDict subclass that represents the type definition and referenced node
    ID of the members of a base type definition. This operates in a similar
    manner to Namespace.

    It contains a mapping of member keys to a tuple of member type and the node
    ID of the member's declaration. By default, the node ID is initialised to
    None. The defaul dictionary operations will act on the type definition only.
    All operations relating to the node ID should be done via the specific
    `*_member_node_id` functions.
    """

    def __init__(self, dict_values=None):
        if dict_values:
            for k, v in dict_values.items():
                super().__setitem__(k, (v, None))

    def __deepcopy__(self, memo):
        # Custom implementation of deepcopy due to incorrect nesting
        c = MemberInfoDict()
        memo[id(self)] = c
        for k, v in self.items():
            c[k] = v[0]
            c.set_member_node_id(k, v[1])
        return c

    def __setitem__(self, attr, obj):
        super().__setitem__(attr, (obj, None))

    def __getitem__(self, key):
        return super().__getitem__(key)[0]

    def get_types(self):
        return [v[0] for v in self.values()]

    def get_types_with_key_dict(self):
        return {k: v[0] for k, v in self.items()}

    def get_types_with_key_list(self):
        return list((k, v[0]) for k, v in self.items())

    def set_member_node_id(self, key, node_id):
        v = super().__getitem__(key)
        if v:
            super().__setitem__(key, (v[0], node_id))

    def get_member_node_id(self, key):
        return super().__getitem__(key)[1]

    def get_member_node_id_with_key_dict(self):
        return {k: v[1] for k, v in self.items()}
