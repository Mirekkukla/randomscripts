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
"""

import datetime
import os
import spending_utils as utils

RAW_DATA_FOLDER_PATH = os.path.join(utils.get_base_folder_path(), "raw_data")

def main():
    utils.optionally_create_dir(utils.get_extracted_tx_folder_path())

    for raw_filename in utils.get_raw_filenames():
        raw_filepath = os.path.join(RAW_DATA_FOLDER_PATH, raw_filename)
        print "Running for '{}'".format(raw_filepath)

        raw_lines_with_header = utils.load_from_file(raw_filepath)
        filtered_raw_lines = filter_tx_lines(raw_lines_with_header[4:])

        converted_tx_lines = converted_to_tx_format(filtered_raw_lines)
        extracted_filepath = utils.get_extracted_tx_filepath(raw_filename)
        utils.write_to_file(converted_tx_lines, extracted_filepath)


def filter_tx_lines(raw_lines):
    """ Remove tx outside of our desired date interval. Return filtered list """
    print "Dropping tx outside of [{}, {}]".format(utils.FIRST_TX_DATE.date(), utils.LAST_TX_DATE.date())
    filtered_lines = []
    for line in raw_lines:
        date_str = line.split(",")[0].strip('"') # "MM/DD/YYYY"
        date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        if date >= utils.FIRST_TX_DATE and date <= utils.LAST_TX_DATE:
            filtered_lines.append(line)
        else:
            print "Nuking {}".format(line)

    total_removed = len(raw_lines) - len(filtered_lines)
    print "Removed {} transactions".format(total_removed)
    return filtered_lines


def converted_to_tx_format(lines):
    """
    Input: list of tx lines in the raw format, e.g:
    "01/27/2019","ATM","","CSAS Taboritska 16/24 Praha","$50.17","","$56.26"

    Output: list of "tx format" lines ordered by ascending date. Format:
    [date]\t[[type] + [description]]\t[deposit / withdrawal amount with no '$' sign]
    (where values don't have the surrounding quotes)

    Return list of converted lines
    """
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

        tsv_line = "{}\t{}\t{}".format(date_str, combined_desc_str, amt_str)
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[0], '%m/%d/%Y'))
    return tsv_lines


### TESTS
def tests():
    # converting raw lines: check sorting and handling of "extra" commas
    raw_withdrawal = '"01/27/2019","ATM","","WITHDRAWL YO","$50.17","","$1,256.26"'
    raw_deposit = '"01/26/2019","TRANSFER","","EARLIER DEPOSIT YO","","$1,000.00","$1,256.26"'
    expected = ['01/26/2019\tTRANSFER + EARLIER DEPOSIT YO\t-1,000.00', '01/27/2019\tATM + WITHDRAWL YO\t50.17']
    converted = converted_to_tx_format([raw_withdrawal, raw_deposit])
    if converted != expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(expected, converted))


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.SCHWAB_CHECKING:
        raise Exception("Can only run in schwab checking mode")
    tests()
    main()
