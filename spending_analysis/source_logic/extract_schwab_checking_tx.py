"""
Input: "raw" csv-formated schwab checking transaction data file
Out: tsv-formatted file(s) with date filtered and "cleaned up" transactions

Input format: input file has a 4 header lines, the second of which is a column header:
"Date","Type","Check #","Description","Withdrawal (-)","Deposit (+)","RunningBalance"

Example lines:
"01/29/2019","TRANSFER","","Funds Transfer from Brokerage -2106","","$561.11","$617.37"
"01/27/2019","ATM","","CSAS Taboritska 16/24 Praha","$50.17","","$56.26"

Cleanup and filtering: we want the converted file to resemble the "chase credit extract" format
  - remove header lines
  - remove the quotes around the values
  - ignore all transactions outside of our desired date interval
  - combine the "Type" and "Description" columns
  - choose the non-empty value of "Deposit" / "Withdrawal" for amount and remove the leading "$"
  - prefix a "-" sign to the amout when the value comes from the "Deposit" column
  - the final format should  [date]\t[type + description]\t[withdrawal or -deposit]
  - export as tsv

Process:
  - export checking transactions as csv from schwab website as
  - set spending_utils.OP_MODE to "OperatingMode.SCHWAB_CHECKING"
  - run script

FOLLOWUP: we can ignore the brokerage file, all the transactions should cancel out
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
    Input: list of tx lines in the raw format, e.g:
    "01/27/2019","ATM","","CSAS Taboritska 16/24 Praha","$50.17","","$56.26"

    Output: list of "tx format" lines ordered by ascending date. Format:
    [date]\t[[type] + [description]]\t[deposit / withdrawal amount with no '$' sign]
    (where values don't have the surrounding quotes)

    Return list of converted lines
    """
    lines = raw_lines_with_header[4:]
    tsv_lines = []
    for line in lines:
        # WARNING: there are occasionally commas inside the numeric fields, can't split on ","
        separator = '","'
        num_separators = line.count(separator)
        if not num_separators == 6:
            raise Exception("Line has {} separators: [{}]".format(num_separators, line))

        full_tsv_line = line.replace(separator, '\t').strip('"')

        date_str = full_tsv_line.split('\t')[0]
        type_str = full_tsv_line.split('\t')[1]
        desc_str = full_tsv_line.split('\t')[3]
        combined_desc_str = "{} + {}".format(type_str, desc_str)

        # withdrawals stay positive, deposits need a leading minus sign
        withdrawal_str = full_tsv_line.split('\t')[4]
        deposit_str = full_tsv_line.split('\t')[5]
        amt_str = withdrawal_str[1:] if withdrawal_str else "-" + deposit_str[1:] # remove leading "$"

        tsv_line = "{}\t{}\t{}\t{}".format(date_str, combined_desc_str, amt_str, source_filename)
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[0], '%m/%d/%Y'))
    return tsv_lines


def tests():
    # converting raw lines: check sorting and handling of "extra" commas
    raw_withdrawal = '"01/27/2019","ATM","","WITHDRAWL YO","$50.17","","$1,256.26"'
    raw_deposit = '"01/26/2019","TRANSFER","","EARLIER DEPOSIT YO","","$1,000.00","$1,256.26"'
    expected = ['01/26/2019\tTRANSFER + EARLIER DEPOSIT YO\t-1,000.00\tyo.txt', '01/27/2019\tATM + WITHDRAWL YO\t50.17\tyo.txt']
    converted = convert_to_tx_format(["header1", "header2", "header3", "header4", raw_withdrawal, raw_deposit], "yo.txt")
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.SCHWAB_CHECKING:
        raise Exception("Can only run in schwab checking mode")
    tests()
    main()
