import logging
import os
from sys import argv

import yaml
from lark import Lark

import tree_crawler as tc
from PlantUmlTreeTransformer import PlantUmlTreeTransformer
from output_producer import dump_to_excel


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
        msg_dic = {}
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

    actors = get_actors(in_tree)
    out_tree = []
    tc.collect_nodes_by_type("communication_step", in_tree, out_tree)
    steps = []
    for comm_node in out_tree:
        message_dic = get_message(comm_node)

        step_node = {
            "Consumer": actors[tc.get_token_value(comm_node, "CONSUMER")].replace("\"", ""),
            "Provider": actors[tc.get_token_value(comm_node, "PROVIDER")].replace("\"", ""),
            "Communication Type": get_config()['colors'][tc.get_token_value(comm_node, "COLOR")],
            "Call Message": message_dic["Call Message"],
            "Call Input": message_dic["Call Input"],
            "Call Output": message_dic["Call Output"],
            "Comments": tc.get_first_token(tc.get_first_node_by_type("comment", comm_node))
        }

        steps.append(step_node)

    return steps


def get_config() -> dict:
    with open("../config/diagram_setup.yaml", "r") as setup_file:
        return yaml.safe_load(setup_file, )


if __name__ == '__main__':
    my_args = get_opts(argv)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if '-grammar' in my_args:
        grammar_file = open(my_args['-grammar'])
        parser = Lark(grammar_file, debug=True)
    else:
        exit(1)

    if '-file' in my_args:
        f = open(my_args['-file'])
    else:
        exit(1)

    if '-pic' in my_args:
        pic_loc = my_args['-pic']

    if '-v' in my_args:
        logging.basicConfig(level=logging.INFO)

    tree_transformed = PlantUmlTreeTransformer().transform(parser.parse(f.read()))
    steps = process_comm_steps(tree_transformed)

    if '-output' in my_args:
        dump_to_excel(steps, my_args['-output'])
