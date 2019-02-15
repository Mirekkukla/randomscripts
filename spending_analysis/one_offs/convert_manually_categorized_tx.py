"""
One-off script to port manually categorized tx lines
from the old chase credit format to the new

Input: the old manual categorizations file and the new uncategorized lines file
Output: a new manual categorizations file

Usage:
- make sure "old" manually categorized tx file exists
- run the "export uncategorized tx" script on the new data
- make sure the resulting uncategorized tx file exists
- tun this script
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

#pylint: disable=wrong-import-position
from source_logic import spending_utils as utils
#pylint: enable=wrong-import-position

new_folder = utils.get_single_source_folder_path(utils.OperatingMode.CHASE_CREDIT)
uncategorized_lines = utils.load_from_file(os.path.join(new_folder, "uncategorized_lines.tsv"))

old_folder = utils.get_single_source_folder_path(utils.OperatingMode.OLD_CHASE_CREDIT)
old_manually_categorized = utils.load_from_file(os.path.join(old_folder, "manually_categorized_tx.tsv"))

if not uncategorized_lines or not old_manually_categorized:
    raise Exception("Failed to load data")

new_categorized_filepath = os.path.join(new_folder, "manually_categorized_tx.tsv")
if os.path.exists(new_categorized_filepath):
    raise Exception("New manually categorized file shouldn't exist, that's what we're making")

new_manually_categorized = []
still_uncategorized = []
for line in uncategorized_lines:
    date = line.split('\t')[0]
    desc = line.split('\t')[1]
    amt = line.split('\t')[2]
    source = line.split('\t')[3]

    old_category = None
    for old_line in old_manually_categorized:

        # old format takes in raw .txt files, new format takes in raw .csv files
        sources_match = old_line and source.replace(".csv", ".txt")
        # old format has commas for thousands, new format doesn't
        amt_wo_leading_zero = amt[1:] if amt[0] == "0" else amt
        amounts_match = amt_wo_leading_zero in old_line.replace(",", "")

        if date in old_line and sources_match and amounts_match: # we have a match!
            if not old_category:
                old_category = old_line.split('\t')[-1]
                new_manually_categorized.append(line + "\t" + old_category)
            elif old_category == old_line.split('\t')[-1]:
                # duplicate match, but it has the same category so we're all good
                continue
            else:
                raise Exception("Duplicate match for '{}': first match was '{}', second is '{}'".format(line, old_category, old_line))
    if not old_category:
        still_uncategorized.append(line)


if not still_uncategorized:
    print "Wheee, all categorized"
    utils.write_to_file(new_manually_categorized, new_categorized_filepath)
else:
    print "Remaining {} lines without matches:".format(len(still_uncategorized))
    print still_uncategorized
