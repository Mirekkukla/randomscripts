"""
This script helps you find keywords that can be used to categorize tx,
and makes it easier to iterate on manual categorization. The resulting keywords
and manual categorizations will be used by another script export the final fully
categorized data.

Input: a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`

Workflow:

1. Finding candidate keywords "distributions":
- make sure `per_line_query` is empty
- uncomment one of the two `print_distribution` lines and run script
- choose a promising term showing up in a frequently occuring desciption
- set the term as the value for `per_line_query` and run script
- if no false positives show up, add the term to the "terms" dictionary

2. Iterating with manual overrides (once term list is pretty fixed):
- run script (which will export a `remaining_lines.tsv` file)
- paste the exported file contents into google sheets
- categorize additional transactions manually in google sheets
- copy contents from google sheets and replace contents of `new_categorized_tx.tsv`
- repeat

Manual categorizations from previous loop iterations are maintaed in `old_categorizations.tsv`

Once there are no more `remaining_lines.tsv` you can move to the final export step.
"""

import os
import re
from chase_extract_tx import BASE_FOLDER
from chase_extract_tx import convert_to_tsv


# terms with spaces are deliberate so as to minimize false positives
# terms with substrinfs of read words are meant to capture variations on a word
terms = {
    'CNC': ["TRAVEL CREDIT", "AUTOMATIC PAYMENT", "ANNUAL MEMBERSHIP FEE"],

    # flight, train, uber, other transport
    'F': ["airline", "FRONTIER", " air ", "UNITED 0", "PEGASUS", "NORWEGIAN", "KIWI.COM", "RYANAIR"],
    'TR': ["WWW.CD.CZ", "AMTRAK", "LE.CZ", "CALTRAIN"],
    'UB': ["uber", "LYFT"],
    'OT': ["limebike", "BIRD", "PARKING KITTY", "MTA", "CITY OF PORTLAND DEPT", "76 -", "fuel", "HUB", "CHEVRON", "SHELL"],

    # housing, activity
    'H': ["AIRBNB", "hotel"],
    'A': ["VIATOR"], # visas go in here too

    # coffee, restaurant, booze, store
    'C': ["coffee", "costa", "starbucks", "philz", "java", "LOFT CAFE", "Tiny's", "KAFE", "KAVA", "STUMPTOWN", "COFFE"],
    'R': ["restaur", "sushi", "BILA VRANA", "pizza", "grill", "AGAVE", "thai", "ramen", "bagel", "pub ",
           "taco", "VERTSHUSET", "MIKROFARMA", "LTORGET", "POULE", "CHIPOTLE", "BIBIMBAP", "Khao", "EAST PEAK",
           "ZENBU", "EUREKA", "KERESKEDO", "CRAFT", "BURGER", "BAO", "ESPRESSO", "CAFE", "house",
           "PHO", "pizz", "REST", "TAVERN"],
    'B': ["brew", "liquor", "beer", "PUBLIC HO", "TAPROOM", "wine", "VINOTEKA", "PONT OLOMOUC", "BAR ", "hops",
           "BOTTLE", " PIV", "POPOLARE", "NELSON", "GROWLERS", "HOP SHOP", "BARREL", "BLACK CAT", "VENUTI",
           "BODPOD", "VINEYARD", "MIKKELLER", "CANNIBAL"],
    'S': ["Billa", "ALBERT", "market", "SAFEWAY", "CVS", "GROCERY", "CENTRA", "Strood", "DROGERIE", "WHOLEFDS", "FOOD", "RITE"],

    # entertainment (gifts-books-games)
    'E': ["AMAZON", "POWELL", "NINTENDO", "GOPAY.CZ", "FREEDOM INTERNET", "AMZN", "FLORA", "BARNES"],
    # body (clothes-hair-spa),
    'BDY': ["NORDSTROM", "spa", "ALEXANDRA D GRECO", "FIT FOR LIFE", "MANYOCLUB"],
    # digital (vpn-spotify-website-phone)
    'DIG': ["AVNGATE", "Spotify", "GHOST", "google"],
    'EDU': ["CZLT.CZ"], # language-course / EFT course / license renewal
    'MOV': [], # moving
    'HLT': [], # insurance, doctors, etc
    'HMM': [], # sketchy shit
    'I': [], # unknown small charge, ignore
    '?' : [] # unknown, return to later
}

def main():
    all_terms = reduce(lambda l1, l2: l1 + l2, terms.values())
    per_line_query = None
    remaining_lines = []
    match_count = 0
    categorized_count = 0

    new_categorized_tx_path = os.path.abspath(BASE_FOLDER + "new_categorized_tx.tsv")
    categorizations = load_new_categorized_tx(new_categorized_tx_path)

    old_categorizations_path = os.path.abspath(BASE_FOLDER + "old_categorizations.tsv")
    # update_with_old_categorizations(categorizations, old_categorizations_path)

    lines = load_all_tx_lines()
    check_tsv_tx_format(lines)
    check_no_bogus_categorizations(categorizations, lines)

    for line in lines:

        # manual categorizations
        if line in categorizations:
            categorized_count += 1
            continue

        # term matching
        if substring_match(line, all_terms):
            match_count += 1
            continue
        
        remaining_lines.append(line)

        per_line_query = "" # searching for a specific candidate term
        if per_line_query and substring_match(line, [per_line_query]):
            print line


    # if not per_line_query: # if not searching for a specific term, print distribution
    #     print_distribution(get_desc_distribution(remaining_lines, all_terms))
        # print_distribution(get_word_distribution(remaining_lines, all_terms))

    print "\nTotal lines: {}".format(len(lines))
    print "- Manually categorized: {}".format(categorized_count)
    print "- Matched a term: {}".format(match_count)
    print "- Remaining: {}".format(len(remaining_lines)) 

    # export remaining lines into CSV form manual fill-in in google sheets
    remaining_lines_filepath = os.path.abspath(BASE_FOLDER + "remaining_lines.tsv")
    write_to_file(remaining_lines, remaining_lines_filepath)

    # replace old manually categorized file
    old_categorizations_as_list = [desc + "\t" + category for desc, category in categorizations.iteritems()]
    write_to_file(old_categorizations_as_list, old_categorizations_path)


# FILE READING AND WRITING


# returns a map from {line (w/o categorizaion) -> categorization}
def load_new_categorized_tx(filepath):
    raw_lines = load_from_file(filepath)
    lines = fix_gdocs_number_formatting(raw_lines)

    check_tsv_tx_format(lines, with_category=True)
    categorizations = {}
    for line in lines:
        category = line.split("\t")[-1] # fourth column is empty if there's no manual category
        if not category:
            continue
        if category not in terms:
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


# mutates `categorizations`
def update_with_old_categorizations(categorizations, filepath):
    lines = load_from_file(filepath)
    total_added = 0
    for line in lines:
        naked_line = line.split("\t")[-1]
        category = line.rsplit("\t", 1)[0]
        if category not in terms:
            raise Exception("Bad category '{}' in '{}'".format(category, line))

        if naked_line not in categorizations:
            categorizations[naked_line] = category
            total_added += 1
    print "Added {} additional old categorizations\n".format(total_added)


def load_all_tx_lines():
    filepath_to_read = os.path.abspath(BASE_FOLDER + "soph_2018_tx.tsv")
    filepath_to_write = os.path.abspath(BASE_FOLDER + "all_2018_categorized_tx.tsv")

    lines = load_from_file(filepath_to_read)

    # TEMPTEMPTEMPTMEP
    lines += load_from_file(filepath_to_read.replace("soph", "mirek"))

    if not lines:
        raise Exception("Didn't find any tx lines, something is wrong")

    print "Loaded {} total tx lines".format(len(lines))
    return lines


def load_from_file(filepath):
    if not os.path.exists(filepath):
        print "No file at {}, ignoring".format(filepath)
        return []

    print "Loading lines from {}".format(filepath)
    with open(filepath) as f_read:
        lines = f_read.read().splitlines()
        print "Loaded {} lines".format(len(lines))
        return lines


def write_to_file(lines, filepath):
    with open(filepath, "w") as f:
        for line in lines:
            f.write(line + "\n")
    print "\nWrote {} lines to\n{}".format(len(lines), filepath)


# SANITY CHECKS

def check_tsv_tx_format(lines, with_category=False):
    leading_date_exp = r'^[0-9]{2}/[0-9]{2}' # "MM/DD"
    number_exp = r'[-]{0,1}[0-9,]*\.[0-9]{2}' # "-1,234.56"
    end_of_line_exp = r'\t[A-Z]{1,3}$' if with_category else r'$' # "EDU"
    tsv_tx_expr = leading_date_exp + r'\t.*\t' + number_exp + end_of_line_exp

    for line in lines:
        if not re.match(tsv_tx_expr, line):
            print "Split on tab: {}".format(line.split('\t'))
            raise Exception("Line not in tsv tx format: '{}'".format(line))

    print "Passed tsv tx format check"


def check_no_bogus_categorizations(categorizations, lines):
    """ Makes sure every manual categorization corresponds to an actual tx """
    lines_as_set = set(lines)
    for categorized_line in categorizations.keys():
        if categorized_line not in lines_as_set:
            print [categorized_line]
            raise Exception("Bogus categorized line: '{}'".format(categorized_line))

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


def get_amt(line):
    return float(line.split("\t")[-1].replace(",", ""))


# DISTRIBUTION LOGIC

def get_desc_distribution(lines, terms_to_filter_out):
    desc_count = {}
    for line in lines:
        desc = line.split("\t")[1].upper()
        if desc not in desc_count:
            desc_count[desc] = 0
        desc_count[desc] += 1
    return desc_count


def get_word_distribution(lines, terms_to_filter_out):
    word_count = {}
    for line in lines:
        if substring_match(line, terms_to_filter_out):
            continue
        desc = line.split("\t")[1].upper()
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
