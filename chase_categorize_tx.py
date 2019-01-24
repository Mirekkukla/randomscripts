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
    with open(filepath_to_read, "r") as f_read:
        lines = f_read.read().splitlines()

    # count how many times each description occurs
    desc_count = {}

    for line in lines:

        # cancel out CC fees
        if substring_match(line, ["TRAVEL CREDIT"]):
            continue

        # payments / transfers
        if substring_match(line, ["AUTOMATIC PAYMENT"]):
            continue

        # terms with spaces are deliberate so as to minimize false positives

        flight_terms = ["airline", "FRONTIER", " air ", "UNITED 0", "PEGASUS"]
        commute_terms = ["uber", "limebike", "LYFT", "WWW.CD.CZ", "BIRD", "PARKING KITTY", "LE.CZ", "MTA", "CALTRAIN", "CITY OF PORTLAND DEPT", "76 -", "fuel"]
        housing_terms = ["AIRBNB", "hotel"]
        activity_terms = ["VIATOR"]

        coffee_terms = ["coffee", "costa", "starbucks", "philz", "java", "LOFT CAFE", "Tiny's"]
        restaurant_terms = ["restaur", "sushi", "BILA VRANA", "pizza", "grill", "AGAVE", "thai", "ramen", "bagel", "pub ", "taco"]
        alcohol_terms = ["brew", "liquor", "beer", "PUBLIC HO", "TAPROOM", "wine", "VINOTEKA", "PONT OLOMOUC", "BAR ", "hops", "BOTTLE"]
        grocery_terms = ["Billa", "ALBERT", "market", "SAFEWAY", "CVS", "GROCERY"]

        books_games_gifts_movies_terms = ["AMAZON", "POWELL", "NINTENDO", "GOPAY.CZ", "FREEDOM INTERNET", "FLORA"]
        vpn_spotify_website_phone_terms = ["AVNGATE", "Spotify", "GHOST", "google"]

        if substring_match(line, alcohol_terms + commute_terms + coffee_terms +
                           restaurant_terms + housing_terms + grocery_terms +
                           books_games_gifts_movies_terms + vpn_spotify_website_phone_terms +
                           activity_terms + flight_terms):
            continue

        if substring_match(line, ["FOODS"]):
            print line

        desc = line.split("\t")[1]
        if desc not in desc_count:
            desc_count[desc] = 0
        desc_count[desc] += 1

    print_description_count(desc_count)
    print "Total left: {}".format(sum(int(v) for v in desc_count.values()))


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
