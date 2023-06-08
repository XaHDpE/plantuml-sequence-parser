import argparse
import os

from sequenceparser import sequenceparser_core
from sequenceparser.helpers.lark_helper import get_sequence_tree_transformed
from sequenceparser.helpers.output_producer import dump_to_excel

from src import sequenceparser


def execute():
    parser = argparse.ArgumentParser()
    parser.add_argument("-inputFile", type=str, required=True)
    parser.add_argument("-outputDir", type=str, required=True)
    args = parser.parse_args()

    input_full_fpath = args.inputFile
    f = open(input_full_fpath)

    seq_tree_transformed = get_sequence_tree_transformed(f.read())
    steps = sequenceparser_core.process_comm_steps(seq_tree_transformed)

    out_path_dir = args.outputDir
    input_file_name = os.path.split(input_full_fpath)[1]
    file_name, file_extension = os.path.splitext(input_file_name)
    out_excel_file = os.path.join(out_path_dir, str(file_name) + ".xlsx")
    dump_to_excel(steps, out_excel_file)


if __name__ == "__main__":
    execute()
