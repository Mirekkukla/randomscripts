"""
This script helps you find keywords that can be used to categorize tx,
creates a template you can use to create manual categorizations,
and sanity checks the resulting file to ensure full coverage.

Input: a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`
Output: `REMAINING_LINES_FILENAME` tsv file, consisting of lines that don't have coverage


Workflow:

1. Find keywords that can be used to auto-categorize transactions:
- make sure `GREP_QUERY` is empty
- uncomment one of the two `print_distribution` lines and run script
- choose a promising term showing up in a frequently occuring desciption
- set the term as the value for `GREP_QUERY` and run script
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
import spending_utils as utils
import load_manual_categorized_tx

# MODIFY THIS WHILE ITERATING
# (We'll print out all un-categorized lines that match it)
GREP_QUERY = ""

UNCATEGORIZED_LINES_FILENAME = "uncategorized_lines.tsv"

def main():
    uncategorized_lines = []
    match_count = 0
    categorized_count = 0

    lines = utils.load_all_tx_lines()
    categorizations = load_manual_categorized_tx.safely_get_manual_categorizations(lines)

    print "Categorizing all lines\n"
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

        if GREP_QUERY and substring_match(line, [GREP_QUERY]):
            print line

    # if not searching for a specific term, print distribution of remaining lines
    if not GREP_QUERY and uncategorized_lines:
        all_terms = reduce(lambda l1, l2: l1 + l2, utils.get_terms().values(), [])
        print_distribution(get_desc_distribution(uncategorized_lines, all_terms), "Desc distribution")
        print_distribution(get_word_distribution(uncategorized_lines, all_terms), "Word distribution")

    print "Total lines processed: {}".format(len(lines))
    print "Total categorized: {}".format(categorized_count + match_count)
    print "- Manually categorized: {}".format(categorized_count)
    print "- Matched a term: {}".format(match_count)
    print "Remaining: {}".format(len(uncategorized_lines))

    # export remaining lines into TSV which will get copy-pasted to google sheets and manually populated
    uncategorized_lines_filepath = os.path.join(utils.get_base_folder_path(), UNCATEGORIZED_LINES_FILENAME)
    if uncategorized_lines:
        utils.write_to_file(uncategorized_lines, uncategorized_lines_filepath)
    else:
        print "All lines are categorized"
        if os.path.isfile(uncategorized_lines_filepath):
            print "Nuking existing file at {}".format(uncategorized_lines_filepath)
            os.remove(uncategorized_lines_filepath)


# TEXT PROCESSING

def substring_match(line_str, naive_candidate_substrings):
    """
    Return true iff one of the strings in the `candidate_substrings` array is
    a subtring of `line_str`. Matches are considered on a case-insensitive basis
    """
    if not isinstance(naive_candidate_substrings, list):
        raise Exception("Didn't pass an array")

    # careful to not filter everything if the given candidate substring list is e.g ["blah", ""]
    candidate_substrings = [s for s in naive_candidate_substrings if s]
    if not candidate_substrings:
        return False

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
    for category, keywords in utils.get_terms().iteritems():
        if not keywords:
            continue
        if substring_match(line_str, keywords):
            return category
    return None


# DISTRIBUTION LOGIC

def get_desc_distribution(lines, terms_to_filter_out):
    desc_count = {}
    for line in lines:
        if substring_match(line, terms_to_filter_out):
            continue
        desc = line.split('\t')[1]
        if desc not in desc_count:
            desc_count[desc] = 0
        desc_count[desc] += 1
    return desc_count


def get_word_distribution(lines, terms_to_filter_out):
    word_count = {}
    for line in lines:
        if substring_match(line, terms_to_filter_out):
            continue
        desc = line.split('\t')[1]
        for word in desc.split():
            if word not in word_count:
                word_count[word] = 0
            word_count[word] += 1
    return word_count


def print_distribution(count_by_desc, distibution_desc):
    recurring_items = {desc: count for desc, count in count_by_desc.iteritems() if count >= 3}
    if recurring_items:
        print "{}: ".format(distibution_desc)
        for desc, count in sorted(recurring_items.iteritems(), key=lambda (k, v): v):
            print "{}: {}".format(desc, count)
    else:
        print "{} is empty".format(distibution_desc)
    print ""


if __name__ == "__main__":
    main()
