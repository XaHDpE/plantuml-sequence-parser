from lark import Lark

from plantuml_grammar_parser.helpers.ref_files_helper import get_grammar_sequence
from plantuml_grammar_parser.transformers.PlantUmlTreeTransformer import PlantUmlTreeTransformer


def get_sequence_tree_transformed(grammar_instance_text):
    grammar_file = get_grammar_sequence()
    parser = Lark(grammar=grammar_file)
    return PlantUmlTreeTransformer().transform(parser.parse(grammar_instance_text))
