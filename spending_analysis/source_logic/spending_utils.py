import datetime
import os
import re

class OperatingMode(object): #pylint: disable=too-few-public-methods
    CHASE_CREDIT = "CHASE_CREDIT"
    CHASE_CHECKING = "CHASE_CHECKING"
    SCHWAB_CHECKING = "SCHWAB_CHECKING"
    SCHWAB_BROKERAGE = "SCHWAB_BROKERAGE"

# MODIFY THIS DEPENDING ON WHAT DATA WE'RE PROCESSING
# WARNING: this is a global var and gets changed by the final aggregate export script
# GOTCHA: don't find this global as a default arg, otherwise it's initial value will get "fixed"!
OP_MODE = OperatingMode.CHASE_CREDIT

FIRST_TX_DATE = datetime.datetime(2019, 5, 1)

# NOTE: we're effectively not using the last tx date anymore
LAST_TX_DATE = datetime.datetime(9999, 12, 31) # last date we have data across all sources

BASE_FOLDER = os.path.join(os.path.expanduser("~"), "spending_analysis_05_2020")

# TODO: randomize and check for multiple matches

# terms with surrounding whitespace are deliberate so as to minimize false positives
# terms with substrings of read words are meant to capture variations on a word
# GOTCHA: make sure to escape special chars, as these will be part of a regex
chase_credit_terms = {
    'CNC': ["TRAVEL CREDIT", "AUTOMATIC PAYMENT", "ANNUAL MEMBERSHIP FEE",
            "Payment Thank You"],

    # flight, train, uber, other transport
    'F': ["airline", "FRONTIER", " air ", "air\t", "UNITED 0", "UNITED      0", "PEGASUS", "NORWEGIAN", r"KIWI\.COM", "RYANAIR"],
    'TR': [r"WWW\.CD\.CZ", "AMTRAK", r"LE\.CZ", "CALTRAIN"],
    'UB': ["uber", "LYFT"],
    'OT': ["limebike", "BIRD", "PARKING KITTY", "MTA", "CITY OF PORTLAND DEPT", "76 -", "fuel", "HUB",
           "CHEVRON", "SHELL", "JUMPBIKESHARESAMOLACA", "SMARTPARK", "BIKETOWN", "RAZOR SCOOTER",
           "SPACE AGE"],

    # housing, activities
    'H': ["AIRBNB", "hotel", "MOTEL"],
    'A': ["VIATOR"], # visas go in here too

    # coffee, restaurant, booze, store
    'C': ["coffee", "costa", "starbucks", "philz", "java", "LOFT CAFE", "Tiny's", "KAFE", "KAVA", "STUMPTOWN",
          "COFFE", "PULP-PAPA", "ROASTERS", "FIGLIA", "DUTCH BROS"],
    'R': ["restaur", "sushi", "BILA VRANA", "pizza", "grill", "AGAVE", "thai", "ramen", "bagel", "pub ", "pub\t",
          "taco", "VERTSHUSET", "MIKROFARMA", "LTORGET", "POULE", "CHIPOTLE", "BIBIMBAP", "Khao", "EAST PEAK",
          "ZENBU", "EUREKA", "KERESKEDO", "CRAFT", "BURGER", "BAO", "ESPRESSO", "CAFE",
          "PHO", "pizz", " REST", "TAVERN", "TAQUERIA", "ANKENY", "BLUE GOOSE", "MODERN TIMES", "CANTEEN",
          "CRACK LLC", "LARDO", "YATAIMURA", "WHOLEFDS", "POSTMATES", "MOBERI", "WHOLE BOWL", "NORANEKO",
          "KITCHEN", "JUICING", "BISTRO", "DRAGON", "XINH", "VIRTUOUS", "POKE", "CHICKEN"],

    'B': ["brew", "liquor", "beer", "PUBLIC HO", "TAPROOM", "wine", "VINOTEKA", "PONT", "BAR ", "hops",
          "BOTTLE", " PIV", "\tPIV", "POPOLARE", "NELSON", "GROWLERS", "HOP SHOP", "BARREL", "BLACK CAT", "VENUTI",
          "BODPOD", "VINEYARD", "MIKKELLER", "CANNIBAL", "FRESHBAR", "bar\t", "FONTEINEN", "QUICKIE PICKIE",
          "BELMONT", "LOYAL LEGION", "EASTBURN", "HEREAFTER", "BEULAHLAND", "CIDER"],

    'S': ["Billa", "ALBERT", "market", "SAFEWAY", "CVS", "7-ELEVEN", "GROCERY", "Strood", "DROGERIE", "WHOLEFDS",
          "FOOD", "RITE", "MERCADO", "MASOJIKO FRANCOUZSK", "PLAID PANTRY", "FRED MEYER", "QUICK STORE"],

    # entertainment (gifts-books-games)
    'E': ["AMAZON", "POWELL", "NINTENDO", r"GOPAY\.CZ", "FREEDOM INTERNET", "AMZN", "FLORA", "BARNES", "THEATER",
          "POWELL'S"],

    # body (clothes-hair-spa),
    'BDY': ["NORDSTROM", r"\sspa\s", "ALEXANDRA D GRECO", "FIT FOR LIFE", "MANYOCLUB", "RODANFI"],

    # subscription (vpn-spotify-website-phone)
    'SUB': ["AVNGATE", "Spotify", "GHOST", "PROJECT FI", "Google Fi", "HMA PRO VPN"],

    # misc
    'ONE': ["Google Storage", r"GOOGLE \*Domains"], # one-offs (laptop, phone)
    'EDU': [r"CZLT\.CZ"], # language-course / EFT course / license renewal
    'HLT': ["World Nomads", "AGILE INS", "DENTAL", "PROVIDENCE", "INSURANCE", "MYBENEFITSKEEPER"], # insurance, doctors, etc
    'HMM': ["NETFLIX"], # sketchy shit
    'I': [], # unknown small charge, ignore

    # wedding
    'W': ["Etsy", "COSTCO COM"],

    # bills
    'BILL': ["COMCAST", "PORTLAND GNL ELEC"],

    # Moving (furniture, etc)
    'M': ["WAL-MART"],

    # Interest charges
    'FEE': ["INTEREST CHARGE", "PURCH INTEREST"]
}

chase_checking_terms = {
    'CNC': ["CHASE CREDIT CRD AUTOPAY", "SCHWAB", "DEPOSIT", "TRANSFER", "TAX", "C PAYROLL",
            "payment from MIROSLAV", "payment to Sophia", "payment from VERONIKA KUKLA", "POPMONEY",
            "Payment to Chase card", "FID BKG SVC LLC  MONEYLINE",
            "PAYROLL", "payment to Sophia", "payment from SOPHIA", "payment to Miroslav"],
    'ATM': ["ATM", "CHECK_PAID"],
    'ONE': ["WIRE FEE", "Pacific Gas"],
    'FEE': ["ATM FEE", "ADJUSTMENT FEE", "SERVICE FEE", "COUNTER CHECK"],
    'SQR': ["SQC*", "VENMO", "payment from SUZANNE", "payment to Mom", "payment to Suzy"],
    'F': ["NORWEGIAN", "EXPEDIA", "payment from FRANK"],
    'HMM': ["PIZTUZTIYA"],
    'TR': ["RAIL"],

    'C': ["ROASTER"],
    'R': ["sushi"],

    'RNT': ["1299.28"],
    'W': ["125.00"]

}

schwab_checking_terms = {
    'CNC': ["TRANSFER", "ACH"],
    'ATM': ["ATM"],
    'FEE': ["INTADJUST"],
    'F': ["LAN.COM"]
}

schwab_brokerage_terms = {
    'CNC': ["TRANSFER", "VANGUARD"],
    'FEE': ["Interest"]
}


# TERM-SPECIFIC STUFF

def get_terms(mode=None):
    if not mode:
        mode = OP_MODE
    terms_by_mode = {
        OperatingMode.CHASE_CREDIT: chase_credit_terms,
        OperatingMode.CHASE_CHECKING: chase_checking_terms,
        OperatingMode.SCHWAB_CHECKING: schwab_checking_terms,
        OperatingMode.SCHWAB_BROKERAGE: schwab_brokerage_terms
    }
    return terms_by_mode[mode]

def get_all_legal_categories():
    all_mode_values = [v for k, v in OperatingMode.__dict__.iteritems() if not k.startswith('__')]
    categories = set()
    for mode_value in all_mode_values:
        listed_categories_for_mode = get_terms(mode_value).keys()
        categories.update(listed_categories_for_mode)
    return categories


# PATH-RELATED STUFF

def get_single_source_folder_path(mode=None):
    if not mode:
        mode = OP_MODE
    folder_by_mode = {
        OperatingMode.CHASE_CREDIT: "chase_extract_credit_data",
        OperatingMode.CHASE_CHECKING: "chase_extract_checking_data",
        OperatingMode.SCHWAB_CHECKING: "schwab_extract_checking_data",
        OperatingMode.SCHWAB_BROKERAGE: "schwab_extract_brokerage_data"
    }
    return os.path.join(BASE_FOLDER, folder_by_mode[mode])

def get_aggregate_folder_path():
    return os.path.join(BASE_FOLDER, "aggregate_data")

def get_extracted_tx_folder_path():
    return os.path.join(get_single_source_folder_path(), "extracted_data")


def get_raw_filenames(mode=None):
    if not mode:
        mode = OP_MODE
    files_by_mode = {
        OperatingMode.CHASE_CREDIT: ["mirek_raw.csv", "soph_raw.csv"],
        OperatingMode.CHASE_CHECKING: ["mirek_checking_raw.csv", "soph_checking_raw.csv"],
        OperatingMode.SCHWAB_CHECKING: ["mirek_schwab_checking_raw.csv"],
        OperatingMode.SCHWAB_BROKERAGE: ["mirek_schwab_brokerage_raw.csv"],
    }
    return files_by_mode[mode]


def get_extracted_tx_filepath(raw_filename, mode=None):
    if not mode:
        mode = OP_MODE

    if "raw.csv" not in raw_filename:
        raise Exception("Bad raw filename: '{}'".format(raw_filename))

    tx_filename = raw_filename.replace("raw.csv", "tx.tsv")
    return os.path.join(get_extracted_tx_folder_path(), tx_filename)


# FILE READING / WRITING

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
    if not lines:
        print "\nNo lines given, writing to {}".format(filepath)
        return

    with open(filepath, "w") as f:
        for line in lines:
            f.write(line + "\n")
    print "\nWrote {} lines to:\n{}".format(len(lines), filepath)


# TX-FORMAT SPECIFIC STUFF

def run_extraction_loop(convert_to_tx_format_fn, should_write_to_file=True):
    """ The main loop run by the "extraction" scripts. It's behavior is controlled by OP_MODE """
    extracted_folder_path = get_extracted_tx_folder_path()
    if not os.path.exists(extracted_folder_path):
        print "Folder at '{}' doesn't exist, creating it".format(extracted_folder_path)
        os.makedirs(extracted_folder_path)

    raw_data_folder_path = os.path.join(get_single_source_folder_path(), "raw_data")
    final_lines = []
    for raw_filename in get_raw_filenames():
        raw_filepath = os.path.join(raw_data_folder_path, raw_filename)
        print "Running extraction loop for '{}'".format(raw_filepath)

        raw_lines_with_header = load_from_file(raw_filepath)
        converted_tx_lines = convert_to_tx_format_fn(raw_lines_with_header, raw_filename)
        filtered_tx_lines = filter_tx_lines(converted_tx_lines)

        if not filtered_tx_lines:
            print "No transactions from processing {}, nothing to export\n".format(raw_filename)
            continue

        if should_write_to_file:
            extracted_filepath = get_extracted_tx_filepath(raw_filename)
            write_to_file(filtered_tx_lines, extracted_filepath)

        final_lines += filtered_tx_lines
        print ""

    return final_lines


def filter_tx_lines(tx_lines):
    """ Remove tx outside of our desired date interval. Return filtered list """
    print "Dropping tx outside of [{}, {}]".format(FIRST_TX_DATE.date(), LAST_TX_DATE.date())
    filtered_lines = []
    for line in tx_lines:
        date_str = line.split("\t")[0] # "MM/DD/YYYY"
        date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        if date >= FIRST_TX_DATE and date <= LAST_TX_DATE:
            filtered_lines.append(line)
        else:
            print "Nuking {}".format(line)

    total_removed = len(tx_lines) - len(filtered_lines)
    print "Removed {} transactions".format(total_removed)
    return filtered_lines


def load_all_tx_lines():
    raw_filenames = get_raw_filenames()
    print "Loading all extracted tx lines from {}".format(raw_filenames)
    lines = []
    for raw_filename in raw_filenames:
        filepath_to_read = get_extracted_tx_filepath(raw_filename)
        lines += load_from_file(filepath_to_read)

    if not lines:
        raise Exception("Didn't find any tx lines, something is wrong")

    print "Loaded {} total tx lines".format(len(lines))
    check_tsv_tx_format(lines)
    return lines


# SANITY CHECKS

def check_tsv_tx_format(lines, with_category=False):
    """
    Our tx format is:
    [DD/MM/YYYY]\t[description]\t[amount with 2 decimal places]\t[raw file source]'

    If `with_category` is true, there's one more "category" column at the end
    """
    leading_date_exp = r'^[0-9]{2}/[0-9]{2}/[0-9]{4}' # "DD/MM/YYYY"
    number_exp = r'[-]{0,1}[0-9,]*\.[0-9]{2}' # "-1,234.56"
    end_of_line_exp = r'\t[A-Z]{1,4}$' if with_category else r'$' # "EDU"
    tsv_tx_expr = leading_date_exp + r'\t.*\t' + number_exp + r'\t.*' + end_of_line_exp
    for line in lines:
        if line.split('\t') == ['', '', '', '', '']:
            continue
        if not re.match(tsv_tx_expr, line):
            print "Split on tab: {}".format(line.split('\t'))
            raise Exception("Line not in tsv tx format, check number decimal points: [{}]".format(line))

    print "Passed tsv tx format check"
