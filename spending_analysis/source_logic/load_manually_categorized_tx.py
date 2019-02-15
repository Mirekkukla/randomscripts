"""
Load the tsv file of manually-categorized tx that was copy/pasted
from google docs. Make sure the format is reasonable.

Load the full list of uncategorized tx. Make sure there every
"manually" categorized tx actually matches an uncategorized
tx in the source data.
"""

import os
import source_logic.spending_utils as utils

MANUALLY_CATEGORIZED_TX_FILENAME = "category_overrides.tsv"

def main():
    print "RUNNING FROM MAIN: only loads categorizations to sanity check all is well\n"
    lines = utils.load_all_tx_lines()
    safely_get_manual_categorizations(lines)


def safely_get_manual_categorizations(lines):
    manual_tx_path = os.path.join(utils.get_aggregate_folder_path(), MANUALLY_CATEGORIZED_TX_FILENAME)
    categorizations = load_categorized_tx(manual_tx_path)
    check_categorizations_coverage(categorizations, lines)
    return categorizations


# returns a map from {line (w/o categorizaion) -> categorization}
def load_categorized_tx(filepath):
    print "Loading manually categorized tx"
    raw_lines = utils.load_from_file(filepath)
    utils.check_tsv_tx_format(raw_lines, with_category=True)
    lines = raw_lines
    if utils.OP_MODE == utils.OperatingMode.OLD_CHASE_CREDIT:
        lines = fix_gdocs_number_formatting(raw_lines)

    categorizations = {}
    for line in lines:
        source = line.split("\t")[3]
        filenames = utils.get_raw_filenames()
        if source not in filenames:
            continue

        category = line.split("\t")[-1]
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


def fix_gdocs_number_formatting(manually_categorized_lines):
    """
    Google docs prefixes a zero to amts < 1 dollar, whereas the old chase format doesn't
    This method removed the learing zeros
    """
    if utils.OP_MODE != utils.OperatingMode.OLD_CHASE_CREDIT:
        raise Exception("Leaving zeroes should only be remove for OLD_CHASE_CREDIT mode")

    fixed_lines = []
    for line in manually_categorized_lines:
        [date_str, desc, amt_str, source, category] = line.split('\t')
        if amt_str[0] != "0":
            fixed_lines.append(line)
            continue

        fixed_amt_str = amt_str[1:]
        fixed_line = '\t'.join([date_str, desc, fixed_amt_str, source, category])
        fixed_lines.append(fixed_line)

    return fixed_lines


def tests():
    print "Running google formatting test"
    # test gdocs format fixing
    good_line = "02/21/2018\tI'M GOOD\t.88\tyo.txt\tCNC"
    bad_line = "02/21/2018\tNEED FIXING\t0.99\tyo.txt\tCNC"
    expected = ["02/21/2018\tI'M GOOD\t.88\tyo.txt\tCNC", "02/21/2018\tNEED FIXING\t.99\tyo.txt\tCNC"]
    converted = fix_gdocs_number_formatting([good_line, bad_line])
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))
    print "Test passed\n"


if __name__ == '__main__':
    if utils.OP_MODE == utils.OperatingMode.OLD_CHASE_CREDIT:
        tests()
    main()
