import os
import re
from enum import Enum


# needs to live here so that there's not a circular dependency between the
# "create categorization logic" file and "load manual categorizations" file
CATEGORIES = ['A', 'C', 'B', 'E', 'F', 'I', 'H', 'DIG', 'TR', 'MOV', 'HMM', 'S', 'R', 'HLT', 'CNC', 'EDU', 'OT', 'BDY', 'UB']

# TODO: change to depend
BASE_FOLDER_PATH = os.path.abspath("/Users/mirek/chase_checking_extract_data/")
EXTRACTED_TX_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, "extracted_data")
MANUALLY_CATEGORIZED_TX_FOLDER_PATH = os.path.join(BASE_FOLDER_PATH, "manually_categorized_data")

class OperatingMode(object): #pylint: disable=too-few-public-methods
    CHASE_CREDIT = 1
    CHASE_CHECKING = 2

# MODIFY THIS DEPENDING ON WHAT YOU'RE DOING
CURRENT_OPERATING_MODE = OperatingMode.CHASE_CHECKING

def get_raw_filenames():
    if CURRENT_OPERATING_MODE == OperatingMode.CHASE_CREDIT:
        return ["mirek_2018_raw.txt", "soph_2018_raw.txt"]
    elif CURRENT_OPERATING_MODE == OperatingMode.CHASE_CHECKING:
        return ["mirek_checking_2018_raw.txt", "soph_checking_2018_raw.txt"]
    else:
        raise Exception("Unknown operating mode '{}'".format(CURRENT_OPERATING_MODE))

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
    print "Loading all extracted tx lines"
    lines = []
    for raw_filename in get_raw_filenames():
        tx_filename = get_extracted_tx_filename(raw_filename)
        filepath_to_read = os.path.join(EXTRACTED_TX_FOLDER_PATH, tx_filename)
        lines += load_from_file(filepath_to_read)

    if not lines:
        raise Exception("Didn't find any tx lines, something is wrong")

    print "Loaded {} total tx lines\n".format(len(lines))
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
