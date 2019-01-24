"""
Load a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`.
Try to categorize each transaction by examining the description.
- If we succeed, append a cell to the csv row with the category
- If not, leave the row unchanged

Export the resulting data as a new .tsv
"""

import os
import re

def main():

    base_folder = "/Users/mirek/temp/"
    filepath_to_read = os.path.abspath(base_folder + "mirek_2018_tx.tsv")
    filepath_to_write = os.path.abspath(base_folder + "mirek_2018_categorized_tx.tsv")

    lines = None
    with open(filepath_to_read) as f_read:
        lines = f_read.read().splitlines()


    for line in lines:

        if "brew" in line.lower():
            continue

        if "uber" in line.lower():
            continue

        coffee_terms = ["coffee", "costa", "starbucks", "philz", "java"]
        if substring_match(line, coffee_terms):
            continue

        food_terms = ["restaur", "sushi"]
        if substring_match(line, food_terms):
            continue

        if "" in line.lower():
            print line

        # continue

        # print line

def substring_match(line_str, candidate_substrings):
    """
    Return true iff one of the strings in the `candidate_substrings` array is
    a subtring of `line_str`. Matches are considered on a case-insensitive basis
    """
    expr = ".*({}).*".format("|".join(candidate_substrings).lower())
    if re.match(expr, line_str.lower()):
        return True
    return False

if __name__ == "__main__":
    main()
