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
- copy contents from google sheets and replace contents of `new_categorized_tx.txt`
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
    manually_categorized_count = 0

    # if new categorization conflict with old, we'll keep the old
    new_categorized_tx_path = os.path.abspath(BASE_FOLDER + "new_categorized_tx.txt")
    categorizations = load_new_categorized_tx(new_categorized_tx_path)

    old_categorizations_path = os.path.abspath(BASE_FOLDER + "old_categorizations.tsv")
    # update_with_old_categorizations(categorizations, old_categorizations_path)

    lines = load_all_tx_lines()
    for line in lines:

        # manual categorizations
        desc = line.split("\t")[1]
        if desc in categorizations:
            manually_categorized_count += 1
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
    print "- Manually categorized: {}".format(manually_categorized_count)
    print "- Matched a term: {}".format(match_count)
    print "- Remaining: {}".format(len(remaining_lines)) 

    # export remaining lines into CSV form manual fill-in in google sheets
    remaining_lines_filepath = os.path.abspath(BASE_FOLDER + "remaining_lines.tsv")
    write_to_file(remaining_lines, remaining_lines_filepath)

    # replace old manually categorized file
    old_categorizations_as_list = [desc + "\t" + category for desc, category in categorizations.iteritems()]
    write_to_file(old_categorizations_as_list, old_categorizations_path)


# FILE READING AND WRITING

# returns a map from {description -> categorization}
def load_new_categorized_tx(filepath):
    lines = load_from_file(filepath)
    categorizations = {}
    for line in lines:
        category = line.split("\t")[-1] # fourth column is empty if there's no manual category
        if not category:
            continue
        if category not in terms:
            raise Exception("Bad category '{}' in '{}'".format(category, line))

        desc = line.split("\t")[1]
        if desc not in categorizations:
            categorizations[desc] = category

    print "{} lines were categorized\n".format(len(categorizations))
    return categorizations


# mutates `categorizations`
def update_with_old_categorizations(categorizations, filepath):
    lines = load_from_file(filepath)
    total_added = 0
    for line in lines:
        desc = line.split("\t")[0]
        category = line.split("\t")[1]
        if desc not in categorizations:
            categorizations[desc] = category
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

    print "Loaded {} total tx lines\n".format(len(lines))
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
