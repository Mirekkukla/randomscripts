"""
Load a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`.
Import the categorization logic defined in
Try to categorize each transaction by examining the description.
- If we succeed, append a cell to the csv row with the category
- If not, leave the row unchanged

Export the resulting data as a new .tsv file
"""

import os
import chase_create_categorizing_logic as auto_category_logic
import chase_load_manual_categorized as manual_category_logic
import chase_utils as utils

FINAL_CATEGORIZED_FILENAME = "final_categorized_tx.tsv"


def main():
    export()


def export(include_manually_categorized=True):
    if not include_manually_categorized:
        print "WARNING: ignoring manually categorized, this should be used to debug\n"

    final_lines = []
    lines = utils.load_all_tx_lines()
    categorizations = manual_category_logic.safely_get_manual_categorizations(lines)
    for line in lines:

        # manual categorizations
        if line in categorizations:
            if include_manually_categorized:
                final_line = line + '\t' + categorizations[line]
                final_lines.append(final_line)
            continue

        # programatic categorization
        matching_category = auto_category_logic.get_matching_category(line)
        if not matching_category:
            raise Exception("No category given / found for line: '{}'".format(line))

        final_line = line + '\t' + matching_category
        final_lines.append(final_line)

    utils.check_tsv_tx_format(final_lines, True)

    filename = FINAL_CATEGORIZED_FILENAME
    if not include_manually_categorized:
        filename = filename.replace(".tsv", "_without_manually_categorized.tsv")

    final_list_filepath = os.path.join(utils.get_base_folder_path(), filename)
    print "Writing {} fully categorized tx to: \n{}".format(len(final_lines), final_list_filepath)
    utils.write_to_file(final_lines, final_list_filepath)


if __name__ == "__main__":
    main()
