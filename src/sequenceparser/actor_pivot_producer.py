import argparse
import os

from sequenceparser import sequenceparser
from sequenceparser.helpers import dict_helper
from sequenceparser.helpers.lark_helper import get_sequence_tree_transformed


def get_output_dic(dir_path, split_by_typ):
    dic = {}
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            try:
                f_path = os.path.join(root, f)
                with open(f_path, "r") as file:
                    process_seq_file(file, dic, split_by_typ)
            except BaseException as e:
                print(f"Unable to process file {f}, error: {e}")
                raise
    return dic


def process_seq_file(f, dic, split_type_flag):
    f_name = f.name.split("\\")[-1]
    seq_tree_transformed = get_sequence_tree_transformed(f.read())
    steps = sequenceparser.process_comm_steps(seq_tree_transformed)

    if split_type_flag:

        for seq_step in steps:
            cur_prov_node = {}
            if seq_step['Provider'] in dic:
                cur_prov_node = dic[seq_step['Provider']]
            if seq_step['Communication Type'] not in cur_prov_node.keys():
                cur_prov_node.update({ seq_step['Communication Type'] : [seq_step['Call Message'] + " - " + f_name] })
            else:
                cur_value = seq_step['Call Message'] + " - " + f_name
                if cur_value not in cur_prov_node[seq_step['Communication Type']]:
                    cur_prov_node[seq_step['Communication Type']].append(cur_value)

            dic.update({seq_step['Provider']: cur_prov_node})


    if not split_type_flag:

        for seq_step in steps:

            if seq_step['Direction'] == 'Request':
                cur_prov_node = []

                if seq_step['Provider'] in dic:
                    cur_prov_node = dic[seq_step['Provider']]

                cur_value = seq_step['Call Message']

                if cur_value not in cur_prov_node:
                    cur_prov_node.append(cur_value)

                if 'Cross-system' in seq_step['Communication Type']:
                    dic.update({seq_step['Provider']: cur_prov_node})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputDir", type=str, required=True)
    parser.add_argument("--outputFile", type=str, required=True)
    parser.add_argument("--splitByType", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    in_path_dir = args.inputDir
    split_by_type = args.splitByType

    try:
        out_dic = get_output_dic(in_path_dir, split_by_type)
        output_file = args.outputFile

        dict_helper.to_file(out_dic, output_file)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
