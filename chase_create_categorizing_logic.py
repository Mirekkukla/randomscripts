"""
This script helps you find keywords that can be used to categorize tx,
creates a template you can use to create manual categorizations,
and sanity checks the resulting file to ensure full coverage.

Input: a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`
Output: `REMAINING_LINES_FILENAME` tsv file, consisting of lines that don't have coverage


Workflow:

1. Find keywords that can be used to auto-categorize transactions:
- make sure `per_line_query` is empty
- uncomment one of the two `print_distribution` lines and run script
- choose a promising term showing up in a frequently occuring desciption
- set the term as the value for `per_line_query` and run script
- if no false positives show up, add the term to the "terms" dictionary

2. Creating manual overrides (once the term list is pretty fixed):
- run this script (which will export `REMAINING_LINES_FILENAME` tsv file)
- paste the exported file contents into google sheets
- categorize additional transactions manually in google sheets
- copy contents from google sheets and replace contents of `MANUALLY_CATEGORIZED_FILENAME` using vim
  - (GOTCHA: sublime doesn't realize that ".tsv" means "use tab delimiters")
- run this script again to ensure the resulting data is correctly fomatted

3. If there are no more uncategorized transactions, the full list of categorized tx
   is exported to `FINAL_CATEGORIZED_FILENAME`
"""

import os
import re
from chase_utils import terms
import chase_utils as utils
import chase_load_manual_categorized

####TEMPTEMPTEMP: move terms back here from utils

UNCATEGORIZED_LINES_FILENAME = "uncategorized_lines.tsv"
FINAL_CATEGORIZED_FILENAME = "final_categorized_tx.tsv"

def main():
    per_line_query = None
    uncategorized_lines = []
    match_count = 0
    categorized_count = 0

    categorizations = chase_load_manual_categorized.safely_get_categorizations()

    lines = utils.load_all_tx_lines()
    for line in lines:

        # skip manual categorizations
        if line in categorizations:
            categorized_count += 1
            continue

        # try auto-assign a category using term matching
        matching_category = get_matching_category(line)
        if matching_category:
            match_count += 1
            continue

        uncategorized_lines.append(line)

        per_line_query = "" # searching for a specific candidate term
        if per_line_query and substring_match(line, [per_line_query]):
            print line


    if not per_line_query: # if not searching for a specific term, print distribution
        all_terms = reduce(lambda l1, l2: l1 + l2, utils.terms.values())
        print_distribution(get_desc_distribution(uncategorized_lines, all_terms))
        print_distribution(get_word_distribution(uncategorized_lines, all_terms))

    print "\nTotal lines processed: {}".format(len(lines))
    print "Total categorized: {}".format(categorized_count + match_count)
    print "- Manually categorized: {}".format(categorized_count)
    print "- Matched a term: {}".format(match_count)
    print "Remaining: {}\n".format(len(uncategorized_lines))


    # export remaining lines into TSV which will get copy-paster to google sheets and manually populated
    uncategorized_lines_filepath = os.path.join(utils.BASE_FOLDER_PATH, UNCATEGORIZED_LINES_FILENAME)
    if uncategorized_lines:
        utils.write_to_file(uncategorized_lines, uncategorized_lines_filepath)

    elif os.path.isfile(uncategorized_lines_filepath):
        print "No lines remain uncategorized, nuking existing file at {}".format(uncategorized_lines_filepath)
        os.remove(uncategorized_lines_filepath)


# TEXT PROCESSING

def substring_match(line_str, candidate_substrings):
    """
    Return true iff one of the strings in the `candidate_substrings` array is
    a subtring of `line_str`. Matches are considered on a case-insensitive basis
    """
    if not isinstance(candidate_substrings, list):
        raise Exception("Didn't pass an array")

    expr = ".*({}).*".format("|".join(candidate_substrings))
    # note that it'd be more efficient to use re.compile() to compile each regex
    # once outside of line loop (tho this is _plenty_ fast for our purposes)
    if re.match(expr.lower(), line_str.lower()):
        return True
    return False


def get_matching_category(line_str):
    """
    Return the first category (if any) where one of its keywords is
    a subtring of `line_str`, None otherwise
    """
    for category, keywords in terms.iteritems():
        if substring_match(line_str, keywords):
            return category
    return None


# DISTRIBUTION LOGIC

def get_desc_distribution(lines, terms_to_filter_out):
    desc_count = {}
    for line in lines:
        if substring_match(line, terms_to_filter_out):
            continue
        desc = line.split("\t")[1]
        if desc not in desc_count:
            desc_count[desc] = 0
        desc_count[desc] += 1
    return desc_count


def get_word_distribution(lines, terms_to_filter_out):
    word_count = {}
    for line in lines:
        if substring_match(line, terms_to_filter_out):
            continue
        desc = line.split("\t")[1]
        for word in desc.split(" "):
            if word not in word_count:
                word_count[word] = 0
            word_count[word] += 1
    return word_count


def print_distribution(occurance_count_by_desc):
    print "Distribution:"
    for desc, count in sorted(occurance_count_by_desc.iteritems(), key=lambda (k, v): v):
        if count >= 3:
            print "{}: {}".format(desc, count)


if __name__ == "__main__":
    main()
