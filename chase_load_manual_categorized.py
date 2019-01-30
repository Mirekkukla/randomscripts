"""

"""

import os
import chase_utils as utils

MANUALLY_CATEGORIZED_TX_FILENAME = "manually_categorized_tx.tsv"

def main():
    print "RUNNING FROM MAIN: only loads categorizations to sanity check all is well\n"
    safely_get_categorizations()


def safely_get_categorizations():
    manual_tx_path = os.path.join(utils.BASE_FOLDER_PATH, MANUALLY_CATEGORIZED_TX_FILENAME)
    categorizations = load_categorized_tx(manual_tx_path)

    lines = utils.load_all_tx_lines()
    check_no_bogus_categorizations(categorizations, lines)

    return categorizations


# returns a map from {line (w/o categorizaion) -> categorization}
def load_categorized_tx(filepath):
    raw_lines = utils.load_from_file(filepath)
    utils.check_tsv_tx_format(raw_lines, with_category=True)
    lines = fix_gdocs_number_formatting(raw_lines)

    categorizations = {}
    for line in lines:
        category = line.split("\t")[-1] # fourth column is empty if there's no manual category
        if not category:
            continue
        if category not in utils.CATEGORIES:
            raise Exception("Bad category '{}' in '{}'".format(category, line))

        naked_line = line.rsplit("\t", 1)[0]
        categorizations[naked_line] = category

    # note that not all lines are distinct (e.g. "CRUNCH112 800-547-1743 NY")
    print "{} lines ({} distinct) were categorized\n".format(len(lines), len(categorizations))
    return categorizations


def fix_gdocs_number_formatting(raw_lines):
    """ Google docs prefixes a zero to amts < 1 dollar, remove it to match chase """
    fixed_lines = []
    for line in raw_lines:
        number_str = line.split('\t')[-2]
        if number_str[0] == "0":
            chunk_before_num = line.rsplit('\t', 2)[0]
            fixed_num = number_str[1:]
            chunk_after_num = line.split('\t')[-1]

            fixed_line = '\t'.join([chunk_before_num, fixed_num, chunk_after_num])
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    return fixed_lines


def check_no_bogus_categorizations(categorizations, lines):
    """ Makes sure every manual categorization corresponds to an actual tx """
    lines_as_set = set(lines)
    for categorized_line in categorizations.keys():
        if categorized_line not in lines_as_set:
            print [categorized_line]
            raise Exception("Bogus categorized line: '{}'".format(categorized_line))


if __name__ == "__main__":
    main()
