


import os
import re

# terms with spaces are deliberate so as to minimize false positives
# terms with substrinfs of read words are meant to capture variations on a word
terms = {
    'CNC': ["TRAVEL CREDIT", "AUTOMATIC PAYMENT", "ANNUAL MEMBERSHIP FEE"],

    # flight, train, uber, other transport
    'F': ["airline", "FRONTIER", " air ", "UNITED 0", "PEGASUS", "NORWEGIAN", "KIWI.COM", "RYANAIR"],
    'TR': ["WWW.CD.CZ", "AMTRAK", "LE.CZ", "CALTRAIN"],
    'UB': ["uber", "LYFT"],
    'OT': ["limebike", "BIRD", "PARKING KITTY", "MTA", "CITY OF PORTLAND DEPT", "76 -", "fuel", "HUB", "CHEVRON", "SHELL"],

    # housing, activities
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

    # misc
    'EDU': ["CZLT.CZ"], # language-course / EFT course / license renewal
    'MOV': [], # moving
    'HLT': [], # insurance, doctors, etc
    'HMM': [], # sketchy shit
    'I': [] # unknown small charge, ignore
}


BASE_FOLDER_PATH = os.path.abspath("/Users/mirek/chase_extract_data/")
EXTRACTED_TX_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, "extracted_data")
MANUALLY_CATEGORIZED_TX_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, "manually_categorized_data")

RAW_FILENAMES = ["mirek_2018_raw.txt", "soph_2018_raw.txt"]

# TODO: change to file path?
def get_extracted_tx_filename(raw_filename):
    if "raw.txt" not in raw_filename:
        raise Exception("Bad raw filename: '{}'".format(raw_filename))
    return raw_filename.replace("raw.txt", "tx.tsv")


# GENERIC FILE STUFF

def optionally_create_dir(dir_path):
    if not os.path.exists(dir_path):
        print "Folder at '{}' doesn't exist, creating it".format(dir_path)
        os.makedirs(dir_path)


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
    print "\nWrote {} lines to:\n{}".format(len(lines), filepath)


# TX-FORMAT SPECIFIC STUFF

def load_all_tx_lines():
    lines = []
    for raw_filename in RAW_FILENAMES:
        tx_filename = get_extracted_tx_filename(raw_filename)
        filepath_to_read = os.path.join(EXTRACTED_TX_FOLDER_PATH, tx_filename)
        lines += load_from_file(filepath_to_read)

    if not lines:
        raise Exception("Didn't find any tx lines, something is wrong")

    print "Loaded {} total tx lines".format(len(lines))
    check_tsv_tx_format(lines)
    return lines


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
