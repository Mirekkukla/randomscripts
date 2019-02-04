"""
One-off script to port manual categorizations from the
"old" chase credit format to the new

Usage:
- make sure "old" manually categorized lines exist
- run 
"""
import datetime
import os
import spending_utils as utils

new_folder = utils.get_base_folder_path(utils.OperatingMode.CHASE_CREDIT)
with open(os.path.join(new_folder, "uncategorized_lines.tsv")) as f_new_uncat:
    uncategorized_lines = f_new_uncat.read().splitlines()

old_folder = utils.get_base_folder_path(utils.OperatingMode.OLD_CHASE_CREDIT)
with open(os.path.join(old_folder, "manually_categorized_tx.tsv")) as f_old_cat:
    old_manually_categorized = f_old_cat.read().splitlines()

new_manually_categorized = []
still_uncategorized = []
for line in uncategorized_lines:
    date = line.split('\t')[0]
    desc = line.split('\t')[1]
    amt = line.split('\t')[2]

    old_category = None
    for old_line in old_manually_categorized:

        # old format has commas for thousands, new format doesn't
        if date in old_line and amt in old_line.replace(",", ""): # we have a match
            if not old_category:
                old_category = old_line.split('\t')[3]
                new_manually_categorized.append(line + "\t" + old_category)
            elif old_category == old_line.split('\t')[3]:
                # duplicate match, but it has the same category so we're all good
                continue
            else:
                raise Exception("Duplicate match for '{}': first match was '{}', second is '{}'".format(line, match, old_line))
    if not old_category:
        still_uncategorized.append(line)


if not still_uncategorized:
    print "Wheee, all categorized"
    new_categorized_filepath = os.path.join(new_folder, "manually_categorized_tx.tsv")
    utils.write_to_file(new_manually_categorized, new_categorized_filepath)
else:
    print "Remaining lines without matches:"
    print still_uncategorized
