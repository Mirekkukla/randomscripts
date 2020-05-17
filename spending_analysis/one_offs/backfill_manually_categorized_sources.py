"""
Add "sources" to a manaully categorized tx file that was
created without them.

For the old chase checking format, at the end there will still be 3
lines you'll need to manually fix. These lines hava the same
source / amt / date, but each comes from a different source
(one from "mirek" and one from "soph"). As-is the script will
assign both versions the same source ("mirek")

02/16/2018      USPS.COM MOVER'S GUIDE 800-238-3150 TN  1.00    mirek_2018_raw.txt
03/07/2018      THE BARONESS LONG ISLAND C NY   31.40   mirek_2018_raw.txt
03/08/2018      TST* THE GINGERMAN NEW YORK NY  25.23   mirek_2018_raw.txt

Modify the resulting categorized file to have the above sources read "soph"
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

#pylint: disable=wrong-import-position
import source_logic.spending_utils as utils
import source_logic.extract_chase_checking_tx as extract_chase_checking_tx
import source_logic.extract_schwab_checking_tx as extract_schwab_checking_tx
import source_logic.extract_schwab_brokerage_tx as extract_schwab_brokerage_tx
from source_logic.load_manually_categorized_tx import MANUALLY_CATEGORIZED_TX_FILENAME
#pylint: enable=wrong-import-position

if utils.OP_MODE == utils.OperatingMode.CHASE_CREDIT:
    raise Exception("Don't need to backfill chase credit, the old -> new conversion script took care of that")

extraction_fn_by_mode = {
    utils.OperatingMode.CHASE_CHECKING: extract_chase_checking_tx.convert_to_tx_format,
    utils.OperatingMode.SCHWAB_CHECKING: extract_schwab_checking_tx.convert_to_tx_format,
    utils.OperatingMode.SCHWAB_BROKERAGE: extract_schwab_brokerage_tx.convert_to_tx_format,
}

old_filepath = os.path.join(utils.get_single_source_folder_path(), MANUALLY_CATEGORIZED_TX_FILENAME)
new_filepath = os.path.join(utils.get_single_source_folder_path(), MANUALLY_CATEGORIZED_TX_FILENAME + "_new")

source_by_line = {}

# these are in the new format, with source (but no category)
extraction_fn = extraction_fn_by_mode[utils.OP_MODE]
extracted_tx_lines = utils.run_extraction_loop(extraction_fn, False)

if extracted_tx_lines[0].count("\t") != 3:
    print extracted_tx_lines[0].split("\t")
    raise Exception("Extracted line tab count is wrong, did you forget to export with source?")

print "Populating our source dictionary"
for extracted_tx in extracted_tx_lines:
    naked_line = extracted_tx.rsplit("\t", 1)[0] # doesn't have source
    source = extracted_tx.split("\t")[-1]
    source_by_line[naked_line] = source

print "Loaded {} unique lines".format(len(source_by_line))

old_manually_categorized_tx_lines = utils.load_from_file(old_filepath)

if old_manually_categorized_tx_lines[0].count("\t") != 3:
    print old_manually_categorized_tx_lines[0].split("\t")
    raise Exception("Extracted line tab count is wrong, did you already backfill source?")

new_manually_categorized_tx_lines = []

# these are in the old format, with a category
for old_categorized_tx in old_manually_categorized_tx_lines:
    naked_line = old_categorized_tx.rsplit("\t", 1)[0]  # doesn't have category
    category = old_categorized_tx.split("\t")[-1]
    source = source_by_line[naked_line]

    new_categorized_line = "{}\t{}\t{}".format(naked_line, source, category)
    new_manually_categorized_tx_lines.append(new_categorized_line)

print "Updated {} lines with source info".format(len(new_manually_categorized_tx_lines))

utils.write_to_file(new_manually_categorized_tx_lines, new_filepath)
