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
