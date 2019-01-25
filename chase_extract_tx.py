"""
Copy and paste the entire contents of chase statmement pdf.
Extract only those lines that represent transactions and export to tsv new file.

Exacmple of lines we want to extract:
10/05 AUTOMATIC PAYMENT - THANK YOU -3,826.72
09/09 NJT MOBILE 3001 NEWARK NJ 26.00

Example of lines we want to ignore:
Minimum Payment: $25.00
09/21 CZECH KORUNA
175.00 X 0.046171428 (EXCHG RATE)
Previous points balance 193,092

The following observations are important:
- tx amounts don't have dollar signs, and are always preceded by a space
- tx amounts might be negative
- tx lines allways end in ".XX"
- tx amounts might be in the thousands (and thus have commas)

Added as a sanity check:
- tx lines always start with a date "XX/XX"
"""

import re
import os

BASE_FOLDER = "/Users/mirek/temp/"

def main():
    run_for_name_prefix("mirek")
    run_for_name_prefix("soph")


def run_for_name_prefix(prefix):
    print "Running for '{}'".format(prefix)
    # sanity check raw data looks right: grep -n "Payment Due Date" soph_2018_raw.txt
    filepath_to_read = os.path.abspath(BASE_FOLDER + prefix + "_2018_raw.txt")
    filepath_to_write = os.path.abspath(BASE_FOLDER + prefix + "_2018_tx.tsv")

    raw_matches = extract_tx_lines(filepath_to_read)
    matches = filter_leading_tx_lines(raw_matches)
    print "\n".join(matches)

    tab_delimited_matches = convert_to_tsv(matches)
    write_to_file(tab_delimited_matches, filepath_to_write)
    print "Done for {}\n".format(prefix)


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
        if date_str >= "02/15" and date_str <= "12/00":
            print "Removed {} tx".format(i)
            return lines[i:]
        print "Nuking " + line


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
