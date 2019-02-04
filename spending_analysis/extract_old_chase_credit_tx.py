"""
NOTE: turns out scraping tx from statement pdfs isn't necessary.
You can now export more than 5 months of "activity" (there used
to be 5 month limit). Keeping this in case things change.

============================================================

Copy and paste the entire contents of chase statmement pdf.
Extract only those lines that represent transactions ("tx lines"),
convert them to a simpler tx format, and export them to tsv new file.


EXTRACTION DETAILS:

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


EXPORTED FORMAT DETAILS:

The exported lines shouls be tab-delimited and consist of 3 columns:
[date]\t[description]\t[amount]

The "date" string should be format MM/DD/YYYY (we'll have to infer the year)
The "description" and "amount" strings should be as given in the raw tx line
"""

import datetime
import re
import os
import spending_utils as utils


def main():
    utils.run_extraction_loop(convert_to_tx_format)


def convert_to_tx_format(raw_lines_with_tons_of_garbage):
    start_date = None
    end_date = None
    tx_line_regex = r'^[0-9]{2}/[0-9]{2}.*\ [-]{0,1}[0-9,]*\.[0-9]{2}$'

    # first we gotta drop all the non-tx garbage and fix the dates
    raw_tx_lines = []
    for line in raw_lines_with_tons_of_garbage:

        if "Opening/Closing Date" in line:
            # e.g. "Opening/Closing Date 12/10/17 - 01/09/18"
            start_date_str = line.split(" ")[2]
            end_date_str = line.split(" ")[-1]
            start_date = datetime.datetime.strptime(start_date_str, '%m/%d/%y')
            end_date = datetime.datetime.strptime(end_date_str, '%m/%d/%y')
            continue

        if re.match(tx_line_regex, line):
            fixed_date = get_fixed_date_str(line, start_date, end_date)
            tx_line = fixed_date + " " + line.split(" ", 1)[1]
            raw_tx_lines.append(tx_line)

    # convert resulting "raw" tx lines with into our own tsv-based "tx format"
    tsv_lines = []
    for line in raw_tx_lines:
        split_on_space = line.split(" ")
        date_str = split_on_space[0]
        desc_str = " ".join(split_on_space[1:-1])
        amt_stry = split_on_space[-1]

        tsv_line = "{}\t{}\t{}".format(date_str, desc_str, amt_stry)
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[0], '%m/%d/%Y'))
    return tsv_lines


def get_fixed_date_str(raw_line, statement_start_date, statement_end_date):
    """
    Find the date on which the given raw tx line occurs. Since tx lines don't tell
    you the year, we have to determine the year ourselves.

    We do this using the statment end dates. We know that our transaction occurs
    withing the statement interval, and thus has the same year as one (or both)
    of the statement start / end dates.

    Append each of these candidate "transaction year" dates to the yearless transaction
    date, and see if the resulting date is inside the statement interval.

    Unfortunatly, it turns out some transactions can be backdated by as much as 2-3 months,
    and thus occur prior to the statement interval. Thus we'll have to "widen" our interval
    quite a bit to make sure to catch them.
    """
    safe_start_date = statement_start_date - datetime.timedelta(days=90)
    safe_end_date = statement_end_date

    yearless_date_str = raw_line.split(" ")[0] # MM/DD
    date_with_start_year_str = yearless_date_str + "/" + safe_start_date.strftime("%Y") # MM/DD/YYYY
    date_with_end_year_str = yearless_date_str + "/" + safe_end_date.strftime("%Y") # MM/DD/YYYY

    # check if start date has the right year
    date_with_start_year = datetime.datetime.strptime(date_with_start_year_str, '%m/%d/%Y')
    if safe_start_date <= date_with_start_year and date_with_start_year <= safe_end_date:
        return date_with_start_year_str

    # check if end date has the right year
    date_with_end_year = datetime.datetime.strptime(date_with_end_year_str, '%m/%d/%Y')
    if safe_start_date <= date_with_end_year and date_with_end_year <= safe_end_date:
        return date_with_end_year_str

    raise Exception("Tx line outside of statement interval [{} - 90, {}]: {}"
                    .format(statement_start_date.date(), statement_end_date.date(), raw_line))


def tests():
    # converting raw lines: check ignoring non-tx lines, sorting, and date fixing
    non_tx1 = "Minimum Payment: $25.00"
    date_line = "Opening/Closing Date 05/10/18 - 06/09/18"
    non_tx3 = "175.00 X 0.046171428 (EXCHG RATE)"
    in_interval_tx = "05/11 Zabka - Seifertova 455 Praha 3 2.57"
    non_tx2 = "09/21 CZECH KORUNA"
    backdated_tx = "03/15 HONG KONG EXCBG3NK__81870 LANTAU -53.51"
    non_tx4 = "Previous points balance 193,092"

    test1_converted = convert_to_tx_format([non_tx1, date_line, non_tx3, in_interval_tx, non_tx2, backdated_tx, non_tx4])
    test1_expected = ['03/15/2018\tHONG KONG EXCBG3NK__81870 LANTAU\t-53.51',
                      '05/11/2018\tZabka - Seifertova 455 Praha 3\t2.57']
    if test1_converted != test1_expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(test1_expected, test1_converted))

    # test date fixing when the interval straddles the year
    date_line = "Opening/Closing Date 12/10/18 - 01/09/19"
    prior_year_backdated_tx = "12/08 TRAVEL CREDIT $300/YEAR -160.80"
    prior_year_tx = "12/20 SHRUNKEN HEAD SKATEBOARDS PORTLAND OR 149.00"
    latter_year_tx = "01/08 FIGUEROA MOUNTAIN BREWING SANTA BARBARA CA 10.84"

    test2_converted = convert_to_tx_format([date_line, prior_year_backdated_tx, prior_year_tx, latter_year_tx])
    test2_expected = ['12/08/2018\tTRAVEL CREDIT $300/YEAR\t-160.80',
                      '12/20/2018\tSHRUNKEN HEAD SKATEBOARDS PORTLAND OR\t149.00',
                      '01/08/2019\tFIGUEROA MOUNTAIN BREWING SANTA BARBARA CA\t10.84']
    if test2_converted != test2_expected:
        raise Exception("TEST FAIL, expected vs actual: \n{}\n{}".format(test2_expected, test2_converted))


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.OLD_CHASE_CREDIT:
        raise Exception("Can only run in old chase credit mode")
    tests()
    main()
