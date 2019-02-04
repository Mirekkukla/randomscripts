"""
Chase checking statments are wonkily formatted, so we can't copy-paste them like
with credit card statements. Fortunately, we can export transactions in CSV format
going back two years, so that's the file / format we'll use herez.

Input: "raw" csv-formated chase checking transaction data file(s)
Out: tsv-formatted file(s) with date filtered and "cleaned up" transactions

Input format: input file has a header, as shown below with an example line:
Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
DEBIT,09/07/2018,"ATM WITHDRAWAL                       009775  09/07233 3RD A",-100.00,ATM,324.17,,

Cleanup and filtering: we want the converted file to resemble the "chase credit extract" format
  - remove header
  - only keep the "Posting Date," "Description", and "Amount" columns
  - ignore all transactions outside of our desired date interval
  - remove the quotes around the "Description" field contents and strip outer whitespace
  - flip the sign of the "amount" field
  - convert to tsv

Process:
  - export checking transactions as csv from chase website as
  - set spending_utils.OP_MODE to "OperatingMode.CHASE_CHECKING"
  - run script
"""

import datetime
import os
import spending_utils as utils


def main():
    raw_data_folder_path = os.path.join(utils.get_base_folder_path(), "raw_data")
    utils.run_extraction_loop(raw_data_folder_path, converted_to_tx_format)


def converted_to_tx_format(raw_lines_with_header):
    """
    Input: list of tx lines in the raw format, e.g:
    DEBIT,09/07/2018,"ATM WITHDRAWAL                       009775  09/07233 3RD A",-100.00,ATM,324.17,,

    Output: list of "tx format" lines ordered by ascending date. Format:
    [date]\t[description with no surrounding quotes or outer whitespace]\t[amount]
    """
    lines = raw_lines_with_header[1:]
    tsv_lines = []
    for line in lines:
        # WARNING: there are occasionally commas inside the description field, can't split on ","
        if not len(line.split('"')) == 3:
            raise Exception("Line has more than the 2 'description' quotes: '{}'".format(line))

        pre_desc_str = line.split('"')[0]
        desc_str = line.split('"')[1].strip()
        post_desc_str = line.split('"')[-1]

        date_str = pre_desc_str.split(",")[1]
        raw_amount_str = post_desc_str.split(",")[1]
        flipped_amount_str = raw_amount_str[1:] if raw_amount_str[0] == "-" else "-{}".format(raw_amount_str)

        tsv_line = "{}\t{}\t{}".format(date_str, desc_str, flipped_amount_str)
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[0], '%m/%d/%Y'))
    return tsv_lines


def tests():
    # converting raw lines: check sorting and handling of "extra" commas
    simple_raw = 'DEBIT,09/07/2018,"SIMPLE DESC",-100.00,ATM,324.17,,'
    raw_with_comma = 'DEBIT,09/06/2018,"EARLIER DATE, AND COMMA",-100.00,ATM,324.17,,'
    expected = ['09/06/2018\tEARLIER DATE, AND COMMA\t100.00', '09/07/2018\tSIMPLE DESC\t100.00']
    converted = converted_to_tx_format(["header", simple_raw, raw_with_comma])
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.CHASE_CHECKING:
        raise Exception("Can only run in chase checking mode")
    tests()
    main()
