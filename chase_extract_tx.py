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

RAW_DATA_FOLDER_PATH = os.path.join(utils.get_base_folder_path(), "raw_data")

def main():
    utils.optionally_create_dir(utils.get_extracted_tx_folder_path())

    # visually sanity check the raw data: grep -n "Payment Due Date" soph_2018_raw.txt
    # you should see 1-2 dates for each month (depending on statement format)
    for raw_filename in utils.get_raw_filenames():
        raw_filepath = os.path.join(RAW_DATA_FOLDER_PATH, raw_filename)
        print "Running for '{}'".format(raw_filepath)

        raw_matches = extract_tx_lines(raw_filepath)
        matches = filter_leading_tx_lines(raw_matches)
        tab_delimited_matches = convert_to_tsv(matches)

        extracted_filepath = utils.get_extracted_tx_filepath(raw_filename)
        write_to_file(tab_delimited_matches, extracted_filepath)
        print ""


def extract_tx_lines(file_to_read):
    lines = None
    with open(file_to_read, "r") as f_read:
        lines = f_read.read().splitlines()

    matches = []
    for line in lines:
        exp = r'^[0-9]{2}/[0-9]{2}.*\ [-]{0,1}[0-9,]*\.[0-9]{2}$'
        if re.match(exp, line):
            matches.append(line)
            continue

    return matches


def filter_leading_tx_lines(lines):
    """
    HACK: we want to ignore all tx prior to the `FIRST_TX_DATE`. Since the tx data
    starts might start on the prior year, and since tx rows don't have a year listed,
    we'll need to do some hackery to remove the leading transactions. This is fragile
    and might need to be updated for future datasets.

    This logic depends on the given lines being chronological
    Returns the "filtered" list of tx lines
    """
    first_tx_date_yearless = utils.FIRST_TX_DATE.strftime("%m/%d")
    print "Removing leading tx prior to {}".format(first_tx_date_yearless)
    for i, line in enumerate(lines):

        # more hackery: "payment" transactions aren't listed chronologically
        # and might thus trip up are "cutover date" logic
        if "AUTOMATIC PAYMENT" in line:
            continue

        date_str = line.split(" ")[0] # "MM/DD"
        if date_str >= first_tx_date_yearless and date_str <= "12/00":
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
    if utils.OP_MODE != utils.OperatingMode.CHASE_CREDIT:
        raise Exception("Can only run in chase credit mode")
    main()
