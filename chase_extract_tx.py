"""
Copy and paste the entire contents of chase statmement pdf.
Extract only those lines that represent transactions ("tx lines")
and export them to tsv new file.

Exacmple of lines we want to extract:
10/05 AUTOMATIC PAYMENT - THANK YOU -3,826.72
09/09 NJT MOBILE 3001 NEWARK NJ 26.00

Example of lines we want to ignore:
Minimum Payment: $25.00
09/21 CZECH KORUNA
175.00 X 0.046171428 (EXCHG RATE)
Previous points balance 193,092

The following observations are important:
- tx line amounts don't have dollar signs, and are always preceded by a space
- tx line amounts might be negative
- tx lines allways end in ".XX"
- tx line amounts might be in the thousands (and thus have commas)

Added as a sanity check:
- tx lines always start with a date "XX/XX"
"""

import re
import os
import chase_utils as utils

RAW_DATA_FOLDER_PATH = os.path.join(utils.BASE_FOLDER_PATH, "raw_data")

def main():
    utils.optionally_create_dir(utils.EXTRACTED_TX_FOLDER_PATH)

    # visually sanity check the raw data: grep -n "Payment Due Date" soph_2018_raw.txt
    # you should see 1-2 dates for each month (depending on statement format)
    for raw_filename in utils.get_raw_filenames():
        raw_filepath = os.path.join(RAW_DATA_FOLDER_PATH, raw_filename)
        print "Running for '{}'".format(raw_filepath)

        raw_matches = extract_tx_lines(raw_filepath)
        matches = filter_leading_tx_lines(raw_matches)
        print "\n".join(matches)

        tab_delimited_matches = convert_to_tsv(matches)

        extracted_filename = utils.get_extracted_tx_filename(raw_filename)
        extracted_filepath = os.path.join(utils.EXTRACTED_TX_FOLDER_PATH, extracted_filename)
        write_to_file(tab_delimited_matches, extracted_filepath)


def get_raw_filepaths(): # move to raw?
    filenames = ["mirek_2018_raw.txt", "soph_2018_raw.txt"]
    return [os.path.join(RAW_DATA_FOLDER_PATH, name) for name in filenames]

def extract_tx_lines(file_to_read):
    lines = None
    with open(file_to_read, "r") as f_read:
        lines = f_read.read().splitlines()

    matches = []
    # exp = get_tx_line_extraction_regex()
    # exp = r'^[0-9]{2}/[0-9]{2}.*\ [-]{0,1}[0-9,]*\.[0-9]{2}$'
    exp = r'^[0-9]{2}/[0-9]{2}.*'
    for line in lines:
        if re.match(exp, line):
            matches.append(line)
            continue

    return matches


# def get_tx_line_extraction_regex():
#     if utils.CURRENT_OPERATING_MODE == utils.OperatingMode.CHASE_CREDIT:
#         return r'^[0-9]{2}/[0-9]{2}.*\ [-]{0,1}[0-9,]*\.[0-9]{2}$'
#     elif utils.CURRENT_OPERATING_MODE == utils.OperatingMode.CHASE_CHECKING:
#         number_exp = r'[-]{0,1}[0-9,]*\.[0-9]{2}'
#         return r'^[0-9]{2}/[0-9]{2}.*\ [-]{0,1}[0-9,]*\.[0-9]{2}$'

    raise Exception("Unknown operating mode '{}'".format(utils.CURRENT_OPERATING_MODE))


def filter_leading_tx_lines(lines):
    """
    HACK: we want to ignore all tx <= 2/15 (2018), but the tx data
    starts on 12/08 (2018). Since tx rows don't have a date, we'll need
    to do some hackery to remove the leading stuff

    This logic depends on the given lines being chronological
    Returns the "filtered" list of tx lines
    """
    print "Removing leading tx prior to 2/15/18"
    for i, line in enumerate(lines):

        # more hackery: the "payment" line comes before the 12/15/18 txs
        if "AUTOMATIC PAYMENT" in line:
            continue

        date_str = line.split(" ")[0] # "MM/DD"
        if date_str > "02/15" and date_str <= "12/00":
            print "Removed {} tx\n".format(i)
            return lines[i:]
        print "Nuking " + line

    print "Nothing to filter\n"
    return []


def convert_to_tsv(matches):
    clean_lines = []
    for line in matches:
        split_on_space = line.split(" ")
        date = split_on_space[0]
        desc = " ".join(split_on_space[1:-1])
        amt = split_on_space[-1]

        clean_line = "{}\t{}\t{}".format(date, desc, amt)
        clean_lines.append(clean_line)

    return clean_lines


def write_to_file(matches, file_to_write):
    with open(file_to_write, "w") as f_write:
        for tx_line in matches:
            f_write.write(tx_line + "\n")

    print "Wrote {} tx to '{}'".format(len(matches), file_to_write)


if __name__ == '__main__':
    main()
