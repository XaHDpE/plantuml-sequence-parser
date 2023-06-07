import yaml
from importlib_resources import files


def get_grammar_sequence() -> str:
    return files("plantuml_grammar_parser.config").joinpath("plantuml_grammar.ebnf").read_text()


def get_config() -> dict:
    config_txt = files("plantuml_grammar_parser.config").joinpath("diagram_setup.yaml").read_text()
    return yaml.safe_load(config_txt)

