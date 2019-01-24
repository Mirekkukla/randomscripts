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

def main():

    base_folder = "/Users/mirek/temp/"
    filepath_to_read = os.path.abspath(base_folder + "mirek_2018_raw.txt")
    filepath_to_write = os.path.abspath(base_folder + "mirek_2018_tx.tsv")

    matches = extract_tx_lines(filepath_to_read)
    print "\n".join(matches)

    tab_delimited_matches = cleanup_matches(matches)
    write_to_file(tab_delimited_matches, filepath_to_write)


def extract_tx_lines(file_to_read):
    lines = None
    with open(file_to_read, "r") as f_read:
        lines = f_read.read().splitlines()

    matches = []
    for line in lines:
        exp = r'^[0-9]{2}/[0-9]{2}.*\ [-]{0,1}[0-9,]*\.[0-9]{2}$'
        if re.match(exp, line):
            print line
            matches.append(line)

    return matches


def cleanup_matches(matches):
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
