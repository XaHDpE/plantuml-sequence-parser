import lark
from lark.tree import Tree


def collect_nodes_by_type(item_name, in_tree, out_tree):
    if isinstance(in_tree, lark.Tree):
        # print(f"search: {item_name}, curr: {in_tree.data}")
        if item_name == in_tree.data:
            out_tree.append(in_tree)
        for child in in_tree.children:
            collect_nodes_by_type(item_name, child, out_tree)


def get_first_node_by_type(item_name, in_tree) -> lark.Tree:
    if isinstance(in_tree, lark.Tree):
        if item_name == in_tree.data:
            return in_tree
        for child in in_tree.children:
            res = get_first_node_by_type(item_name, child)
            if res is not None:
                return res
    return None


def get_first_child_node(in_tree) -> str | Tree | None:
    if isinstance(in_tree, lark.Tree):
        for child in in_tree.children:
            if type(child) == lark.Tree:
                return child
    return None


def get_token_value(in_tree, token_type):
    if isinstance(in_tree, lark.Tree):
        for token in in_tree.children:
            if isinstance(token, lark.Token) and token_type == token.type:
                return token.value
    return None


def get_first_token(in_tree):
    if isinstance(in_tree, lark.Tree):
        for child in in_tree.children:
            res = get_first_token(child)
            if res is not None:
                return res
    if isinstance(in_tree, lark.Token):
        return in_tree.value
    return None
