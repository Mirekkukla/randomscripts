"""
Create a single final with final categorized tx across numerous
operating modes. Creates a single combined "manual overrides"
file we can backup on google docs.
"""

import os
import export_final_categorized_tx
import spending_utils as utils
from spending_utils import OperatingMode as OPMode

final_filepath = os.path.join(utils.get_final_folder_path(), "all_tx.tsv")

def main():
    all_lines = []
    for op_mode in [OPMode.CHASE_CREDIT, OPMode.CHASE_CHECKING, OPMode.SCHWAB_CHECKING]:
        # HACK: global vars are evil
        print "HACK: former OP_MODE value was {}, changing to {}".format(utils.OP_MODE, op_mode)
        utils.OP_MODE = op_mode
        all_lines += export_final_categorized_tx.get_final_lines()

    print "Loaded all {} lines".format(len(all_lines))
    utils.write_to_file(all_lines, final_filepath)


if __name__ == "__main__":
    main()
