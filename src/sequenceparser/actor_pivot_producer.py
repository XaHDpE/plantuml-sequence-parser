import argparse
import os

from sequenceparser import sequenceparser
from sequenceparser.helpers import dict_helper
from sequenceparser.helpers.lark_helper import get_sequence_tree_transformed


def get_output_dic(dir_path):
    dic = {}
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            try:
                f_path = os.path.join(root, f)
                with open(f_path, "r") as file:
                    process_seq_file(file, dic)
            except BaseException as err:
                print(f"Unable to process file {f}, error: {err}")

    return dic


def process_seq_file(f, dic):
    seq_tree_transformed = get_sequence_tree_transformed(f.read())
    steps = sequenceparser.process_comm_steps(seq_tree_transformed)

    for step in steps:

        if step['Direction'] == 'Request':
            curr_arr = []

            if step['Provider'] in dic:
                curr_arr = dic[step['Provider']]
            cur_value = step['Call Message']

            if cur_value not in curr_arr:
                curr_arr.append(cur_value)

            if 'Cross-system' in step['Communication Type']:
                dic.update({step['Provider']: curr_arr})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-inputDir", type=str, required=True)
    parser.add_argument("-outputFile", type=str, required=True)

    args = parser.parse_args()
    in_path_dir = args.inputDir

    out_dic = get_output_dic(in_path_dir)
    output_file = args.outputFile

    dict_helper.to_file(out_dic, output_file)

