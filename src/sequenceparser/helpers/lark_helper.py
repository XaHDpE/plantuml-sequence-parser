from lark import Lark
from . import ref_files_helper as rh
from sequenceparser.transformers.PlantUmlTreeTransformer import PlantUmlTreeTransformer


def get_sequence_tree_transformed(grammar_instance_text):
    grammar_file = rh.get_grammar_sequence()
    parser = Lark(grammar=grammar_file)
    return PlantUmlTreeTransformer().transform(parser.parse(grammar_instance_text))
