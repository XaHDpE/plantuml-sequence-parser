from plantuml_grammar_parser.helpers import tree_crawler as tc, dict_helper
from plantuml_grammar_parser.helpers.lark_helper import get_sequence_tree_transformed
from plantuml_grammar_parser.helpers.ref_files_helper import get_config


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
            # fallback 'comment' dictionary key, if nothing is found
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
            # "Order Num": idx + 1,
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


def get_dict(plantuml_txt) -> list:
    tree_result = get_sequence_tree_transformed(plantuml_txt)
    return process_comm_steps(tree_result)


