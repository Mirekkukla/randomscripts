
import datetime
import os
import spending_utils as utils


raw_data_folder_path = os.path.join(utils.get_base_folder_path(), "raw_data")






with open(os.path.abspath("/Users/mirek/old_chase_extract_credit_data/uncategorized_lines.tsv")) as f:
    old_categorized = f.read().splitlines()

with open(os.path.abspath("/Users/mirek/chase_extract_credit_data/manually_categorized_tx.tsv")) as f:

