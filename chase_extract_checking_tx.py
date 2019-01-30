# chase pdf are wonky-formatted so we can't extract tx amouts - just dates and descriptions
# we'll process a csv export, but that only include 5 trailing month
# beyond that, we'll extract dates and descriptions from the pdfs, but have to enter the transaction amounts manually



# File has a header. Example first two lines:
# Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
# DEBIT,09/07/2018,"ATM WITHDRAWAL                       009775  09/07233 3RD A",-100.00,ATM,324.17,,

import datetime
import os
import chase_utils as utils

RAW_DATA_FOLDER_PATH = os.path.join(utils.get_base_folder_path(), "raw_data")

def main():
    utils.optionally_create_dir(utils.get_extracted_tx_folder_path())

    for raw_filename in utils.get_raw_filenames():
        raw_filepath = os.path.join(RAW_DATA_FOLDER_PATH, raw_filename)
        print "Running for '{}'".format(raw_filepath)

        raw_lines_with_header = utils.load_from_file(raw_filepath)
        filtered_raw_lines = filter_tx_lines(raw_lines_with_header[1:])

        sorted_tsv_lines = convert_to_sorted_tsv(filtered_raw_lines)
        extracted_filepath = utils.get_extracted_tx_filepath(raw_filename)
        write_to_file(sorted_tsv_lines, extracted_filepath)


def filter_tx_lines(raw_lines):
    """ Remove tx outside of our desired date interval. Return filtered list """
    filtered_lines = []
    for line in raw_lines:
        date_str = line.split(",")[1] # "MM/DD/YYYY"
        date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        if date >= utils.FIRST_TX_DATE and date <= utils.LAST_TX_DATE:
            filtered_lines.append(line)
        else:
            print "Nuking {}".format(line)

    total_removed = len(raw_lines) - len(filtered_lines)
    print "Removed {} transactions".format(total_removed)
    return filtered_lines


def convert_to_sorted_tsv(lines):
    # Recal file format:
    # # Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #
    # DEBIT,09/07/2018,"ATM WITHDRAWAL                       009775  09/07233 3RD A",-100.00,ATM,324.17,,
    # WARNING: commas might be insicde the description, which is in quotes
    tsv_lines = []
    for line in lines:
        if not len(line.split('"')) == 3:
            raise Exception("Line has more than 3 quotes: '{}'".format(line))

        pre_comment_str = line.split('"')[0]
        comment_str = '"' + line.split('"')[1] + '"' # we want to preserve the quotes
        post_comment_str = line.split('"')[-1]

        fixed_pre_comment_str = pre_comment_str.replace(",", "\t")
        fixed_post_comment_str = post_comment_str.replace(",", "\t")

        tsv_line = fixed_pre_comment_str + comment_str + fixed_post_comment_str
        tsv_lines.append(tsv_line)

    tsv_lines.sort(key=lambda l: datetime.datetime.strptime(l.split('\t')[1], '%m/%d/%Y'))
    return tsv_lines


def write_to_file(matches, file_to_write):
    with open(file_to_write, "w") as f_write:
        for tx_line in matches:
            f_write.write(tx_line + "\n")

    print "Wrote {} tx to '{}'".format(len(matches), file_to_write)


if __name__ == '__main__':
    if utils.OP_MODE != utils.OperatingMode.CHASE_CHECKING:
        raise Exception("Can only run in chase checking mode")
    main()
