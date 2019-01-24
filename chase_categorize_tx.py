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

    # count how many times each description occurs
    desc_count = {}

    for line in lines:

        alcohol_terms = ["brew", "liquor", "beer"]
        if substring_match(line, alcohol_terms):
            continue

        travel_terms = ["uber", "limebike"]
        if substring_match(line, travel_terms):
            continue

        coffee_terms = ["coffee", "costa", "starbucks", "philz", "java"]
        if substring_match(line, coffee_terms):
            continue

        food_terms = ["restaur", "sushi"]
        if substring_match(line, food_terms):
            continue

        if substring_match(line, [""]):
            print line


        # continue
        # print line



        desc = line.split("\t")[1]
        if desc not in desc_count:
            desc_count[desc] = 0
        desc_count[desc] += 1

    print_description_count(desc_count)


def substring_match(line_str, candidate_substrings):
    """
    Return true iff one of the strings in the `candidate_substrings` array is
    a subtring of `line_str`. Matches are considered on a case-insensitive basis
    """
    if not isinstance(candidate_substrings, list):
        print "Didn't pass an array"
        exit(0)

    expr = ".*({}).*".format("|".join(candidate_substrings))
    # note that it'd be more efficient to use re.compile() to compile each regex
    # once outside of line loop (tho this is _plenty_ fast for our purposes)
    if re.match(expr.lower(), line_str.lower()):
        return True
    return False

def print_description_count(desc_count):
    for desc, count in sorted(desc_count.iteritems(), key=lambda (k, v): v):
        if count >= 3:
            print "{}: {}".format(desc, count)


if __name__ == "__main__":
    main()
