"""
Input: "raw" csv-formated schwab brokerage transaction data file
Out: tsv-formatted file(s) with date filtered and "cleaned up" transactions

Input format: input file has a 2 header lines, the second of which is a column header:
"Date","Action","Symbol","Description","Quantity","Price","Fees & Comm","Amount",

Example lines:
"01/31/2019","Bank Transfer","","OVERDRAFT TO INVESTOR CHECKING -0426","","","","-$3682.63",
"01/24/2019","Sell","VTI","VANGUARD TOTAL STOCK MARKET ETF","33","$134.93","$2.69","$4450.00",
"01/16/2019 as of 01/15/2019","Bank Interest","","BANK INT 121618-011519 SCHWAB BANK","","","","$0.51",

Note the trailing commas on each line and the weird "as of" date text in the third line

Cleanup and filtering: we want the converted file to resemble the "chase credit extract" format
  - remove header lines
  - remove the quotes around the values
  - fix date values (when there are two, we'll choose the "as of" date)
  - ignore all transactions outside of our desired date interval
  - combine the "Action" and "Description" columns
  - remove the "$" character in the "Amount" field
  - flip the amount sign
  - the final format should  [date]\t[action + description]\t[amount]
  - export as tsv

Process:
  - export transactions as csv from schwab website as
  - set spending_utils.OP_MODE to "OperatingMode.SCHWAB_BROKERAGE"
  - run script
"""

import datetime
import os
import spending_utils as utils

def main():
    utils.run_extraction_loop(convert_to_tx_format)

def convert_to_tx_format(raw_lines_with_header, source_filename):
    """
    Input: list of header lines + tx lines in the raw format, e.g:
    "01/24/2019","Sell","VTI","VANGUARD TOTAL STOCK MARKET ETF","33","$134.93","$2.69","$4450.00",
    "01/16/2019 as of 01/15/2019","Bank Interest","","BANK INT 121618-011519 SCHWAB BANK","","","","$0.51",

    Output: list of "tx format" lines ordered by ascending date. Format:
    [date]\t[[action] + [description]]\t[amount with no '$' sign]
    (where values don't have the surrounding quotes)

    Return list of converted lines
    """
    lines = raw_lines_with_header[2:]
    tsv_lines = []
    for line in lines:
        # WARNING: there are occasionally commas inside the numeric fields, can't split on ","
        separator = '","'
        num_separators = line.count(separator)
        if not num_separators == 7:
            raise Exception("Line has {} separators: [{}]".format(num_separators, line))

        full_tsv_line = line.replace(separator, '\t').strip('"').strip('",')

        raw_date_str = full_tsv_line.split('\t')[0]
        date_str = raw_date_str.split(" as of ")[-1]

        type_str = full_tsv_line.split('\t')[1]
        desc_str = full_tsv_line.split('\t')[3]
        combined_desc_str = "{} + {}".format(type_str, desc_str)

        raw_amt_str = full_tsv_line.split('\t')[7].replace("$", "")
        flipped_amt_str = raw_amt_str[1:] if raw_amt_str[0] == "-" else "-{}".format(raw_amt_str)

        tsv_line = "{}\t{}\t{}\t{}".format(date_str, combined_desc_str, flipped_amt_str, source_filename)
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[0], '%m/%d/%Y'))
    return tsv_lines


def tests():
    # converting raw lines: check sorting and handling of "extra" commas
    simple_raw_line = '"01/16/2019 as of 01/15/2019","Bank Interest","","WEIRD DATES","","","","$0.51",'
    harder_raw_line = '"04/16/2018","Buy","VTI","NEGATIVE AMOUNT, COMMA","110","$137.54","$4.95","-$15134.35",'
    expected = ['04/16/2018\tBuy + NEGATIVE AMOUNT, COMMA\t15134.35\tyo.txt',
                '01/15/2019\tBank Interest + WEIRD DATES\t-0.51\tyo.txt']
    converted = convert_to_tx_format(["header1", "header2", simple_raw_line, harder_raw_line], "yo.txt")
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.SCHWAB_BROKERAGE:
        raise Exception("Can only run in schwab brokerage mode")
    tests()
    main()
