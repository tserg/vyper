from collections import OrderedDict


class MemberInfoDict(OrderedDict):
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
