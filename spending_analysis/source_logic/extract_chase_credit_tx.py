"""
Extract tx data from the csv-formated "activity" export you
can get from the chase site.

Input: "raw" csv-formatted chase transaction ("activity") data file(s)
Out: tsv-formatted file(s) with date filtered and cleaned up transactions

Input format: input file has a header, as shown below with an example line:
Transaction Date,Post Date,Description,Category,Type,Amount
12/28/2018,12/31/2018,STICKERS ASIAN CAFE,Food & Drink,Sale,-11.50

Cleanup and filtering: we want the converted file to resemble the "chase credit extract" format
  - remove header
  - use the "Transaction Date" as the date
  - ignore all transactions outside of our desired date interval
  - flip the sign of the "amount" field
  - convert to tsv

Process:
  - export "activity" as csv from chase website as
  - set spending_utils.OP_MODE to "OperatingMode.CHASE_CREDIT"
  - run script
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

#pylint: disable=wrong-import-position
import datetime
import source_logic.spending_utils as utils
#pylint: enable=wrong-import-position


def main():
    utils.run_extraction_loop(convert_to_tx_format)


def convert_to_tx_format(raw_lines_with_header, source_filename):
    """
    Input: a head line followed by tx lines in the raw format, e.g:
    12/28/2018,12/31/2018,STICKERS ASIAN CAFE,Food & Drink,Sale,-11.50

    Output: list of "tx format" lines ordered by ascending date. Format:
    [date]\t[description]\t[amount]\t[source filename]
    """
    lines = raw_lines_with_header[1:]
    tsv_lines = []
    for line in lines:
        if line.count(',') != 5:
            raise Exception("Line has more than the 5 commas: '{}'".format(line))

        date_str = line.split(",")[0]
        desc_str = line.split(",")[2].strip()
        raw_amount_str = line.split(",")[5]
        flipped_amount_str = raw_amount_str[1:] if raw_amount_str[0] == "-" else "-{}".format(raw_amount_str)

        tsv_line = "{}\t{}\t{}\t{}".format(date_str, desc_str, flipped_amount_str, source_filename)
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[0], '%m/%d/%Y'))
    return tsv_lines


def tests():
    # converting raw lines: check sorting and handling of "extra" commas
    print "Running extraction test"
    simple_raw = "01/12/2018,01/14/2018,GEORGE'S FUEL &amp; AUTO,Gas,Sale,-7.61"
    postivie_amt = "01/11/2018,01/15/2018,TRAVEL CREDIT $300/YEAR,,Adjustment,208.07"
    expected = ["01/11/2018\tTRAVEL CREDIT $300/YEAR\t-208.07\tyo.txt", "01/12/2018\tGEORGE'S FUEL &amp; AUTO\t7.61\tyo.txt"]
    converted = convert_to_tx_format(["header", simple_raw, postivie_amt], "yo.txt")
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))
    print "Test passed\n"


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.CHASE_CREDIT:
        raise Exception("Can only run in chase credit mode")

    tests()
    main()
