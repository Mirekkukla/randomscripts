"""
Load a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`.
Import the categorization logic defined in
Try to categorize each transaction by examining the description.
- If we succeed, append a cell to the csv row with the category
- If not, leave the row unchanged

Export the resulting data as a new .tsv file
"""

import chase_create_categorizing_logic as catlogic


def main():
   per_line_query = None
    remaining_lines = []
    final_lines = []
    match_count = 0
    categorized_count = 0

    categorizations = cat_logic.safely_get_categorizations()

    lines = utils.load_all_tx_lines()
    for line in lines:

        # manual categorizations
        if line in categorizations:
            final_line = line + '\t' + categorizations[line]
            final_lines.append(final_line)
            categorized_count += 1
            continue

        # term matching
        matching_category = get_matching_category(line)
        if matching_category:
            final_line = line + '\t' + matching_category
            final_lines.append(final_line)
            match_count += 1
            continue

        remaining_lines.append(line)

        per_line_query = "" # searching for a specific candidate term
        if per_line_query and substring_match(line, [per_line_query]):
            print line


    # process final lines
    if not remaining_lines:
        final_list_filepath = os.path.join(BASE_FOLDER_PATH, FINAL_CATEGORIZED_FILENAME)
        print "FULL COVERAGE, writing final list to: \n{}".format(final_list_filepath)
        utils.check_tsv_tx_format(final_lines, True)
        write_to_file(final_lines, final_list_filepath)








    lines = catlogic.load_lines()
    print len(lines)
    # write_to_file(remaining_lines, filepath_to_write)


def write_to_file(remaining_lines, filepath_to_write):
    with open(filepath_to_write, "w") as f:
        for line in remaining_lines:
            f.write(line + "\n")
    print "Wrote {} lines to \n{}".format(len(remaining_lines), filepath_to_write)


if __name__ == "__main__":
    main()
