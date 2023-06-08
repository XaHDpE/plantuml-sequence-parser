from typing import Any

from lark import Token, Tree, v_args
from lark.visitors import Transformer_InPlace


def _override_tree_children(tree: "Tree", new_child: Any) -> "Tree":
    """
    Replaces the children of a Tree instance with a single child.
    :param tree: Tree instance to update
    :param new_child: new single child of the tree
    :type tree: Tree
    :type new_child: Any
    :return: the tree instance with its single child
    :rtype: Tree
    """
    tree.children = [new_child]
    return tree


@v_args(tree=True)
class PlantUmlTreeTransformer(Transformer_InPlace):

    @staticmethod
    def diagram_name(tree: "Tree") -> Token:
        first_token = tree.children[0]
        return Token(
                "DOUBLE_QUOTED_STRING",
                "".join([child.value[1:-1] for child in tree.children]),
                first_token.pos_in_stream,
                first_token.line,
                first_token.column,
            )

    def multiline_comment(self, tree: "Tree") -> Tree:
        first_token = tree.children[0]
        return Tree(
            "multiline_comment",
            [
                Token(
                    "TEXT",
                    tree.children[0][3:-3],
                    first_token.pos_in_stream,
                    first_token.line,
                    first_token.column,
                )
            ]
        )