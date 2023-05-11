import logging
import os
from sys import argv

import yaml
from lark import Lark

from transformers.PlantUmlTreeTransformer import PlantUmlTreeTransformer
from helpers.output_producer import dump_to_excel
from helpers import dict_helper, tree_crawler as tc


def get_opts(in_args):
    opts = {}  # Empty dictionary to store key-value pairs.
    while in_args:  # While there are arguments left to parse...
        if in_args[0][0] is '-':  # Found a "-name value" pair.
            # print(argv[0][0])
            if len(in_args) > 1:
                if in_args[1][0] != '-':
                    opts[in_args[0]] = in_args[1]
                else:
                    opts[in_args[0]] = True
            elif len(in_args) == 1:
                opts[in_args[0]] = True

        # Reduce the argument list by copying it starting from index 1.
        in_args = in_args[1:]
    return opts


def get_actors(in_tree):
    actors = {}
    actor_nodes = []
    tc.collect_nodes_by_type("participant", in_tree, actor_nodes)
    for actor_node in actor_nodes:
        actor_name = tc.get_first_token(tc.get_first_node_by_type("participant_name", actor_node))
        actor_alias = tc.get_token_value(actor_node, "CNAME")
        actors.update({actor_alias: actor_name})
    return actors


# TODO: fix this crap
def process_comm_steps(in_tree):
    def get_message(cm_node) -> dict:
        src = tc.get_first_node_by_type("message", cm_node)
        msg_node = tc.get_first_node_by_type("single_message", src)
        if msg_node is None:
            msg_node = tc.get_first_node_by_type("decomposed_message", src)
            msg_dic = {"Call Message": tc.get_first_token(msg_node)}
        else:
            msg_dic = {
                "Call Message": tc.get_first_token(msg_node),
            }

        msg_dic.update(
            {
                "Call Input": tc.get_token_value(msg_node, "CALL_INPUT"),
                "Call Output": tc.get_token_value(msg_node, "CALL_OUTPUT")
            }
        )
        return msg_dic

    def get_comment(cm_node) -> dict:
        src_node = tc.get_first_node_by_type("comment", cm_node)
        comment_text = tc.get_first_token(src_node)
        if dict_helper.valid_yaml_string(comment_text):
            res = dict_helper.from_yaml_string(comment_text)
        else:
            # fallback 'comment' dictionary key, if nothing if found
            res = {"Comment": (comment_text or '')}
        return res

    actors = get_actors(in_tree)
    out_tree = []
    tc.collect_nodes_by_type("communication_step", in_tree, out_tree)
    steps_list = []
    for idx, comm_node in enumerate(out_tree):

        message_dic = get_message(comm_node)
        comment_dic = get_comment(comm_node)

        dir_ind = tc.get_first_child_node(
            tc.get_first_node_by_type("direction_indicator", comm_node)
        ).data

        step_node = {
            "Consumer": actors[tc.get_token_value(comm_node, "CONSUMER")].replace("\"", ""),
            "Provider": actors[tc.get_token_value(comm_node, "PROVIDER")].replace("\"", ""),
            "Communication Type": get_config()['colors'][tc.get_token_value(comm_node, "COLOR")],
            "Direction": dir_ind.title(),
            "Call Message": message_dic["Call Message"],
            "Call Input": message_dic["Call Input"],
            "Call Output": message_dic["Call Output"]
        }

        step_node.update(comment_dic)
        steps_list.append(step_node)

    return steps_list


def get_config() -> dict:
    with open("../config/diagram_setup.yaml", "r") as setup_file:
        return yaml.safe_load(setup_file)


if __name__ == '__main__':
    my_args = get_opts(argv)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if '-grammarFile' in my_args:
        grammar_file = open(my_args['-grammarFile'])
        parser = Lark(grammar_file, debug=True)
    else:
        exit(1)

    if '-inputFile' in my_args:
        input_full_fpath = my_args['-inputFile']
        input_directory_path, input_file_name = os.path.split(input_full_fpath)
        f = open(input_full_fpath)
    else:
        exit(1)

    if '-pic' in my_args:
        pic_loc = my_args['-pic']

    if '-v' in my_args:
        logging.basicConfig(level=logging.INFO)

    tree_transformed = PlantUmlTreeTransformer().transform(parser.parse(f.read()))
    steps = process_comm_steps(tree_transformed)

    if '-outputDir' in my_args:
        out_path_dir = my_args['-outputDir']

        file_name, file_extension = os.path.splitext(input_file_name)
        out_excel_file = os.path.join(out_path_dir, str(file_name) + ".xlsx")
        dump_to_excel(steps, out_excel_file)
