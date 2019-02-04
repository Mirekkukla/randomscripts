"""
One-off script to port manual categorizations from the
"old" chase credit format to the new
"""



import datetime
import os
import spending_utils as utils

with open(os.path.abspath("/Users/{}/chase_extract_credit_data/uncategorized_lines.tsv".format(utils.USER))) as f:
    uncategorized_lines = f.read().splitlines()

with open(os.path.abspath("/Users/{}/old_chase_extract_credit_data/manually_categorized_tx.tsv".format(utils.USER))) as f:
    old_categories_lines = f.read().splitlines()

new_categorized = []
still_uncategorized = []
used_old_cats = []
for line in uncategorized_lines:
    date = line.split('\t')[0]
    desc = line.split('\t')[1]
    amt = line.split('\t')[2]

    match = None
    for old_line in old_categories_lines:

        # old format has commas in the thousands, new format doesn't
        amount_matches = amt in old_line or amt in old_line.replace(",", "")
        if date in old_line and amount_matches:
            if not match:
                match = old_line
                new_categorized.append(line)
                used_old_cats.append(old_line)
            elif old_line.split('\t')[3] == match.split('\t')[3]:
                used_old_cats.append(old_line)
                continue # same category so all good
            else:
                raise Exception("Double match for '{}':\n{}\n{}".format(line, match, old_line))
    if not match:
        still_uncategorized.append(line)


print still_uncategorized
print "Done"

# with open(os.path.abspath("/Users/mirek/chase_extract_credit_data/manually_categorized_tx.tsv")) as f3:
