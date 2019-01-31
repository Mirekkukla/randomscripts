import datetime
import os
import re

class OperatingMode(object): #pylint: disable=too-few-public-methods
    CHASE_CREDIT = 1
    CHASE_CHECKING = 2

# MODIFY THIS DEPENDING ON WHAT DATA WE'RE PROCESSING
OP_MODE = OperatingMode.CHASE_CREDIT

FIRST_TX_DATE = datetime.datetime(2018, 2, 16) # first day of joblessness
LAST_TX_DATE = datetime.datetime(2019, 1, 8) # last date we have data across all sources

# TODO: randomize and check for multiple matches

# terms with spaces are deliberate so as to minimize false positives
# terms with substrinfs of read words are meant to capture variations on a word
credit_terms = {
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
    'S': ["Billa", "ALBERT", "market", "SAFEWAY", "CVS", "7-ELEVEN", "GROCERY", "Strood", "DROGERIE", "WHOLEFDS", "FOOD", "RITE"],

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

checking_terms = {
    'CNC': ["CHASE CREDIT CRD AUTOPAY", "SCHWAB", "DEPOSIT", "TRANSFER", "TAX", "C PAYROLL",
            "payment from MIROSLAV", "payment to Sophia", "payment from VERONIKA KUKLA", "POPMONEY"],
    'ATM': ["ATM", "CHECK_PAID"],
    'MOV': ["WIRE FEE", "Pacific Gas"],
    'FEE': ["ATM FEE", "ADJUSTMENT FEE", "SERVICE FEE", "COUNTER CHECK"],
    'SQR': ["SQC*", "VENMO", "payment from SUZANNE", "payment to Mom", "payment to Suzy"],
    'F': ["NORWEGIAN", "EXPEDIA"],
    'HMM': ["PIZTUZTIYA"],
    'TR': ["RAIL"],

}


def get_terms():
    terms_by_mode = {
        OperatingMode.CHASE_CREDIT: credit_terms,
        OperatingMode.CHASE_CHECKING: checking_terms
    }
    return terms_by_mode[OP_MODE]


# a category might be in e.g. "checking manual overrides" even if it isn't in "checking terms"
def get_all_legal_categories():
    return credit_terms.keys() + checking_terms.keys()

def get_base_folder_path():
    folder_by_mode = {
        OperatingMode.CHASE_CREDIT: "chase_extract_data",
        OperatingMode.CHASE_CHECKING: "chase_extract_checking_data"
    }
    return os.path.abspath("/Users/mirek/" + folder_by_mode[OP_MODE])

def get_extracted_tx_folder_path():
    return os.path.join(get_base_folder_path(), "extracted_data")

def get_manually_categorized_tx_folder_path():
    return os.path.join(get_base_folder_path(), "manually_categorized_data")

def get_raw_filenames():
    files_by_mode = {
        OperatingMode.CHASE_CREDIT: ["mirek_2018_raw.txt", "soph_2018_raw.txt"],
        OperatingMode.CHASE_CHECKING: ["mirek_2018_checking_raw.csv", "soph_2018_checking_raw.csv"]
    }
    return files_by_mode[OP_MODE]


def get_extracted_tx_filepath(raw_filename):
    raw_suffix_by_mode = {
        OperatingMode.CHASE_CREDIT: "raw.txt",
        OperatingMode.CHASE_CHECKING: "raw.csv"
    }
    raw_suffix = raw_suffix_by_mode[OP_MODE]
    if raw_suffix not in raw_filename:
        raise Exception("Bad raw filename: '{}'".format(raw_filename))

    tx_filename = raw_filename.replace(raw_suffix, "tx.tsv")
    return os.path.join(get_extracted_tx_folder_path(), tx_filename)


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
    print "Loading all extracted tx lines"
    lines = []
    for raw_filename in get_raw_filenames():
        filepath_to_read = get_extracted_tx_filepath(raw_filename)
        lines += load_from_file(filepath_to_read)

    if not lines:
        raise Exception("Didn't find any tx lines, something is wrong")

    print "Loaded {} total tx lines".format(len(lines))
    check_tsv_tx_format(lines)
    return lines


def check_tsv_tx_format(lines, with_category=False):
    leading_date_expression_by_mode = {
        OperatingMode.CHASE_CREDIT: r'^[0-9]{2}/[0-9]{2}', # "DD/MM",
        OperatingMode.CHASE_CHECKING: r'^[0-9]{2}/[0-9]{2}/[0-9]{4}' # "DD/MM/YYYY"
    }

    for line in lines:
        leading_date_exp = leading_date_expression_by_mode[OP_MODE]
        number_exp = r'[-]{0,1}[0-9,]*\.[0-9]{2}' # "-1,234.56"
        end_of_line_exp = r'\t[A-Z]{1,3}$' if with_category else r'$' # "EDU"
        tsv_tx_expr = leading_date_exp + r'\t.*\t' + number_exp + end_of_line_exp
        if not re.match(tsv_tx_expr, line):
            print "Split on tab: {}".format(line.split('\t'))
            raise Exception("Line not in tsv tx format, check number decimal points: [{}]".format(line))

    print "Passed tsv tx format check"


def fix_gdocs_number_formatting(manually_categorized_lines):
    """ Google docs prefixes a zero to amts < 1 dollar, remove it to match the export format"""
    fixed_lines = []
    for line in manually_categorized_lines:
        [date_str, desc, amt_str, category] = line.split('\t')
        if amt_str[0] != "0":
            fixed_lines.append(line)
            continue

        fixed_amt_str = amt_str[1:]
        fixed_line = '\t'.join([date_str, desc, fixed_amt_str, category])
        fixed_lines.append(fixed_line)

    return fixed_lines


def tests():
    # test gdocs format fixing
    good_line = "02/21/2018\tI'M GOOD\t.88\tCNC"
    bad_line = "02/21/2018\tNEED FIXING\t0.99\tCNC"
    expected = ["02/21/2018\tI'M GOOD\t.88\tCNC", "02/21/2018\tNEED FIXING\t.99\tCNC"]
    converted = fix_gdocs_number_formatting([good_line, bad_line])
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))


if __name__ == "__main__":
    tests()
