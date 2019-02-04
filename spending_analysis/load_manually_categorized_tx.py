"""
Load the tsv file of manually-categorized tx that was copy/pasted
from google docs. Make sure the format is reasonable.

Load the full list of uncategorized tx. Make sure there every
"manually" categorized tx actually matches an uncategorized
tx in the source data.
"""

import os
import spending_utils as utils

MANUALLY_CATEGORIZED_TX_FILENAME = "manually_categorized_tx.tsv"

def main():
    print "RUNNING FROM MAIN: only loads categorizations to sanity check all is well\n"
    lines = utils.load_all_tx_lines()
    safely_get_manual_categorizations(lines)


def safely_get_manual_categorizations(lines):
    manual_tx_path = os.path.join(utils.get_base_folder_path(), MANUALLY_CATEGORIZED_TX_FILENAME)
    categorizations = load_categorized_tx(manual_tx_path)
    check_categorizations_coverage(categorizations, lines)
    return categorizations


# returns a map from {line (w/o categorizaion) -> categorization}
def load_categorized_tx(filepath):
    print "Loading manually categorized tx"
    raw_lines = utils.load_from_file(filepath)
    utils.check_tsv_tx_format(raw_lines, with_category=True)
    lines = utils.fix_gdocs_number_formatting(raw_lines)

    categorizations = {}
    for line in lines:
        category = line.split("\t")[3]
        if not category:
            raise Exception("No category given: '{}'".format(line))
        if category not in utils.get_all_legal_categories():
            raise Exception("Bad category '{}' in '{}'".format(category, line))

        naked_line = line.rsplit("\t", 1)[0]
        categorizations[naked_line] = category

    # note that not all lines are distinct (e.g. "CRUNCH112 800-547-1743 NY" for chase credit)
    print "{} lines ({} distinct) categorized lines loaded\n".format(len(lines), len(categorizations))
    return categorizations


def check_categorizations_coverage(categorizations, lines):
    """ Makes sure every manual categorization corresponds to an actual tx """
    lines_as_set = set(lines)
    for categorized_line in categorizations.keys():
        if categorized_line not in lines_as_set:
            print "Split on tab: {}".format(categorized_line.split('\t'))
            raise Exception("Bogus categorized line: '{}'".format([categorized_line]))


if __name__ == '__main__':
    main()
