"""
This script helps you find keywords that can be used to categorize tx,
and exports a list of transactions that don't get auto-categorized using
the existing keywords / manual categorizations.

Input: a tsv file of tx lines, as exported by one of the "extract" scripts
Output: tsv file of tx lines that don't have coverage

Workflow to find keywords that can be used to auto-categorize:
- make sure `GREP_QUERY` is empty and run script
- examine the printed distributions and choose a promising term
- set the term as the value for `GREP_QUERY` and run script
- if no false positives show up, add the term to the "terms" dictionary

Once we're comfortable with our set of keywords (ie our "autocategorization" logic),
we'll categorize remaining transactions manually.

Categorizing transactions manually:
- run this script (which will export a tsv file of remaining uncategorized tx)
- paste the file contents into google sheets
- categorize additional transactions manually in google sheets
- copy contents from google sheets and replace contents of our "manually categorized tx" file using vim
  - (GOTCHA: sublime doesn't realize that ".tsv" means "use tab delimiters")
- run this script again to ensure the resulting data is correctly fomatted

Once there are no more uncategorized transactions, you can run the final "export" script
"""

import os
import re
import spending_utils as utils
import load_manually_categorized_tx

# MODIFY THIS WHILE ITERATING
# (We'll print out all lines (that aren't manually categorized) that match it)
# GOTCHA: this is used in a regex, so carefeul with special chars like "*"
GREP_QUERY = "MERCADO"

UNCATEGORIZED_LINES_FILENAME = "uncategorized_lines.tsv"

def main():
    uncategorized_lines = []
    match_count = 0
    categorized_count = 0

    lines = utils.load_all_tx_lines()
    categorizations = load_manually_categorized_tx.safely_get_manual_categorizations(lines)

    print "Categorizing all lines\n"
    for line in lines:

        # skip manual categorizations
        if line in categorizations:
            categorized_count += 1
            continue

        # try auto-assign a category using term matching
        # (unless we're "grepping" to find matches / detect false positives)
        if not GREP_QUERY and get_matching_category(line):
            match_count += 1
            continue

        uncategorized_lines.append(line)

        if GREP_QUERY and substring_match(line, [GREP_QUERY]):
            print line

    # if not searching for a specific term, print distribution of remaining lines
    if not GREP_QUERY and uncategorized_lines:
        all_terms = reduce(lambda l1, l2: l1 + l2, utils.get_terms().values(), [])
        print_distribution(get_desc_distribution(uncategorized_lines, all_terms), "Desciption distribution")
        print_distribution(get_word_distribution(uncategorized_lines, all_terms), "Word distribution")

    print "Total lines processed: {}".format(len(lines))
    print "Total categorized: {}".format(categorized_count + match_count)
    print "- Manually categorized: {}".format(categorized_count)
    print "- Matched a term: {}".format(match_count)
    print "Remaining: {}".format(len(uncategorized_lines))

    if GREP_QUERY:
        print "Grep query is '{}', not touching the uncategorized tx file".format(GREP_QUERY)
        exit(0)

    # export remaining lines into TSV which will get copy-pasted to google sheets and manually populated
    uncategorized_lines_filepath = os.path.join(utils.get_single_source_folder_path(), UNCATEGORIZED_LINES_FILENAME)
    if uncategorized_lines:
        utils.write_to_file(uncategorized_lines, uncategorized_lines_filepath)
    else:
        print "All lines are categorized"
        if os.path.isfile(uncategorized_lines_filepath):
            print "Nuking existing file at {}".format(uncategorized_lines_filepath)
            os.remove(uncategorized_lines_filepath)

    return [uncategorized_lines, uncategorized_lines_filepath]


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
