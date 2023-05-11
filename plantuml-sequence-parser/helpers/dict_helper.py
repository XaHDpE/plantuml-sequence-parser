import yaml


def from_yaml_string(input_str) -> dict:
    return yaml.load(input_str, yaml.FullLoader)


def valid_yaml_string(yaml_str) -> bool:
    try:
        res = from_yaml_string(yaml_str)
        return type(res) == dict
    except Exception:
        return False


def get_value_safe(dict_in, key):
    try:
        return dict_in[key]
    except KeyError:
        return ''
