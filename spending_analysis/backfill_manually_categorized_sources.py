"""
Add "sources" to a manaully categorized tx file that was
created without them.
"""

import os
import spending_utils as utils
from load_manually_categorized_tx import MANUALLY_CATEGORIZED_TX_FILENAME

import extract_old_chase_credit_tx
import extract_chase_checking_tx
import extract_schwab_checking_tx
import extract_schwab_brokerage_tx

if utils.OP_MODE == utils.OperatingMode.CHASE_CREDIT:
	raise Exception("Don't need to backfill chase credit, the old -> new conversion script took care of that")

extraction_fn_by_mode = {
    utils.OperatingMode.OLD_CHASE_CREDIT: extract_old_chase_credit_tx.convert_to_tx_format,
    utils.OperatingMode.CHASE_CHECKING: extract_chase_checking_tx.convert_to_tx_format,
    utils.OperatingMode.SCHWAB_CHECKING: extract_schwab_checking_tx.convert_to_tx_format,
    utils.OperatingMode.SCHWAB_BROKERAGE: extract_schwab_brokerage_tx.convert_to_tx_format,
}

old_filepath = os.path.join(utils.get_base_folder_path(), MANUALLY_CATEGORIZED_TX_FILENAME)
new_filepath = os.path.join(utils.get_base_folder_path(), MANUALLY_CATEGORIZED_TX_FILENAME + "_new")

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