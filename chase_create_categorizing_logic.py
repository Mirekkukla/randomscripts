"""
This script helps you find keywords that can be used to categorize tx.
These keywords will be used by another script to actually categorize and export the data.

Loads a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`.

Workflow:

Try to categorize each tx using existing terms.
"""

import os
import re
from chase_extract_tx import BASE_FOLDER

# terms with spaces are deliberate so as to minimize false positives
# terms with substrinfs of read words are meant to capture variations on a word
terms = {
    'canceled_out': ["TRAVEL CREDIT", "AUTOMATIC PAYMENT"],
    
    # flight, train, uber, other transport
    'FL': ["airline", "FRONTIER", " air ", "UNITED 0", "PEGASUS", "NORWEGIAN", "KIWI.COM", "RYANAIR"],
    'TR': ["WWW.CD.CZ", "AMTRAK", "LE.CZ", "CALTRAIN"],
    'UB': ["uber", "limebike", "LYFT", "BIRD", ],
    'OT': ["PARKING KITTY", "MTA", "CITY OF PORTLAND DEPT", "76 -", "fuel", "HUB", "CHEVRON", "SHELL"],

    # housing, activity
    'H': ["AIRBNB", "hotel"],
    'A': ["VIATOR"],

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

    # entertainment (gifts-books-games), body (clothes-hair-spa),
    # vpn-spotify-website-phone, language-course
    'E': ["AMAZON", "POWELL", "NINTENDO", "GOPAY.CZ", "FREEDOM INTERNET", "AMZN", "FLORA", "BARNES"],
    'BDY': ["NORDSTROM", "spa", "ALEXANDRA D GRECO", "FIT FOR LIFE", "MANYOCLUB"],
    'DIG': ["AVNGATE", "Spotify", "GHOST", "google"],
    'LNG': ["CZLT.CZ"],
    'O' : [] # other
}

def load_manually_categorized():
    filepath = os.path.abspath(BASE_FOLDER + "manually_categorized.tsv")
    print "Loading manually categorized lines from\n{}\n".format(filepath)
    
    lines = None
    with open(filepath) as f_read:
        lines = f_read.read().splitlines()

    categorized_descs = set()
    for line in lines:
        if not line.split("\t")[3]: # fourth column is empty if there's no manual category
            continue
        desc = line.split("\t")[1]
        categorized_descs.add(desc)
    
    return categorized_descs


def main():
    all_terms = reduce(lambda l1, l2: l1 + l2, terms.values())
    per_line_query = None
    remaining_lines = []
    match_count = 0

    lines = load_lines()
    manually_categorized = load_manually_categorized()

    for line in lines:
        desc = line.split("\t")[1]
        if desc in manually_categorized:
            continue

        if substring_match(line, all_terms): # skip if line matches a term
            match_count += 1
            continue
        
        remaining_lines.append(line)

        per_line_query = "asdf" # searching for a specific candidate term
        if per_line_query and substring_match(line, [per_line_query]):
            print line


    if not per_line_query: # if not searching for a specific term, print distribution
        print_distribution(get_desc_distribution(remaining_lines, all_terms))
        # print_distribution(get_word_distribution(remaining_lines, all_terms))

    print "Total lines: {}".format(len(lines))
    print "- Manually categorized: {}".format(len(manually_categorized))
    print "- Matched a term: {}".format(match_count)
    print "- Remaining: {}".format(len(remaining_lines)) 

    # export remaining lines into CSV form for easy manual fill-in

    remaining_lines_filepath = os.path.abspath(BASE_FOLDER + "remaining_lines.tsv")
    with open(remaining_lines_filepath, "w") as f_out:
        for line in remaining_lines:
            f_out.write(line + "\n")
    print "\nRemaining lines at \n{}".format(remaining_lines_filepath)


# FILE READING AND WRITING

def load_lines():
    filepath_to_read = os.path.abspath(BASE_FOLDER + "soph_2018_tx.tsv")
    filepath_to_write = os.path.abspath(BASE_FOLDER + "all_2018_categorized_tx.tsv")

    lines = None
    with open(filepath_to_read, "r") as f_read:
        lines = f_read.read().splitlines()

    # temp
    with open(filepath_to_read.replace("soph", "mirek")) as f2_read:
        lines += f2_read.read().splitlines()

    return lines


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
    for desc, count in sorted(occurance_count_by_desc.iteritems(), key=lambda (k, v): v):
        if count >= 3:
            print "{}: {}".format(desc, count)


if __name__ == "__main__":
    main()
