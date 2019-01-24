"""
Load a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`.
Try to categorize each transaction by examining the description.
- If we succeed, append a cell to the csv row with the category
- If not, leave the row unchanged

Export the resulting data as a new .tsv

Set up to make it easy to populate key word terms. Useful methods

"""

import os
import re

def main():

    base_folder = "/Users/mirek/temp/"
    filepath_to_read = os.path.abspath(base_folder + "soph_2018_tx.tsv")
    filepath_to_write = os.path.abspath(base_folder + "soph_2018_categorized_tx.tsv")

    lines = None
    with open(filepath_to_read, "r") as f_read:
        lines = f_read.read().splitlines()

    # temp
    with open(filepath_to_read.replace("soph", "mirek")) as f2_read:
        lines += f2_read.read().splitlines()

    # terms with spaces are deliberate so as to minimize false positives
    canceled_out_terms = ["TRAVEL CREDIT", "AUTOMATIC PAYMENT"]

    flight_terms = ["airline", "FRONTIER", " air ", "UNITED 0", "PEGASUS", "NORWEGIAN", "KIWI.COM", "RYANAIR"]
    train_terms = ["WWW.CD.CZ", "AMTRAK", "LE.CZ", "CALTRAIN"]
    car_metro_terms = ["uber", "limebike", "LYFT",  "BIRD", "PARKING KITTY", "MTA", "CITY OF PORTLAND DEPT", "76 -", "fuel", "HUB", "CHEVRON"]
    housing_terms = ["AIRBNB", "hotel"]
    activity_terms = ["VIATOR"]

    coffee_terms = ["coffee", "costa", "starbucks", "philz", "java", "LOFT CAFE", "Tiny's", "KAFE", "KAVA", "STUMPTOWN"]
    restaurant_terms = ["restaur", "sushi", "BILA VRANA", "pizza", "grill", "AGAVE", "thai", "ramen", "bagel", "pub ",
                        "taco", "VERTSHUSET", "MIKROFARMA", "LTORGET", "POULE", "CHIPOTLE", "BIBIMBAP", "Khao", "EAST PEAK",
                        "ZENBU", "EUREKA", "KERESKEDO", "CRAFT", "BURGER", "BAO", "ESPRESSO", "CAFE", "house"]
    alcohol_terms = ["brew", "liquor", "beer", "PUBLIC HO", "TAPROOM", "wine", "VINOTEKA", "PONT OLOMOUC", "BAR ", "hops",
                     "BOTTLE", " PIV", "POPOLARE", "NELSON", "GROWLERS", "HOP SHOP", "BARREL", "BLACK CAT", "VENUTI",
                     "BODPOD", "VINEYARD"]
    grocery_terms = ["Billa", "ALBERT", "market", "SAFEWAY", "CVS", "GROCERY", "CENTRA", "Strood", "DROGERIE"]

    books_games_gifts_terms = ["AMAZON", "POWELL", "NINTENDO", "GOPAY.CZ", "FREEDOM INTERNET", "AMZN", "FLORA", "BARNES"]
    clothes_hair_spa_terms = ["NORDSTROM", "spa", "ALEXANDRA D GRECO", "FIT FOR LIFE", "MANYOCLUB"]
    vpn_spotify_website_phone_terms = ["AVNGATE", "Spotify", "GHOST", "google"]
    language_course_terms = ["CZLT.CZ"]

    all_terms = canceled_out_terms + alcohol_terms + car_metro_terms + coffee_terms + train_terms + \
                restaurant_terms + housing_terms + grocery_terms + \
                books_games_gifts_terms + vpn_spotify_website_phone_terms + \
                activity_terms + flight_terms + language_course_terms + clothes_hair_spa_terms

    per_line_query = None
    remaining_lines = []
    for line in lines:
        if substring_match(line, all_terms): # skip if line matches a term
            continue
        else:
            remaining_lines.append(line)

        per_line_query = "" # searching for a specific candidate term
        if per_line_query and substring_match(line, [per_line_query]):
            print line


    if not per_line_query: # if not searching for a specific term, print distribution
        # print_historgram(get_desc_distribution(remaining_lines, all_terms))
        print_historgram(get_word_distribution(remaining_lines, all_terms))

    print "Total left: {}".format(len(remaining_lines))


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

# METHODS TO HELP FIND ADDITIONAL LABEL KEYWORDS

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


def print_historgram(occurance_count_by_desc):
    for desc, count in sorted(occurance_count_by_desc.iteritems(), key=lambda (k, v): v):
        if count >= 3:
            print "{}: {}".format(desc, count)


if __name__ == "__main__":
    main()
