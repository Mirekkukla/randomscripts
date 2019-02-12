"""
Load the single file of all aggregate tx
Enrich each tx with country information
and fix dates for flights and hotels
such that the "date" they're stamped with
is the date the expense is realized (ie flight
date / date of the hotel stay).

This helps us find out how much we're spending by
country / over time.
"""

import os
import datetime
import spending_utils as utils

final_spending_path = os.path.join(os.path.expanduser("~"), "final_spending")

basic_tx_path = os.path.join(final_spending_path, "all_tx.tsv")
enriched_tx_path = os.path.join(final_spending_path, "enriched_tx.tsv")
date_overrides_path = os.path.join(final_spending_path, "date_overrides.tsv")


def main():
    basic_tx = utils.load_from_file(basic_tx_path)
    date_overrides = set(utils.load_from_file(date_overrides_path))
    sanity_check_date_overrides(basic_tx, date_overrides)

    enriched_tx = []


    for tx in basic_tx:
        raw_date = tx.split('\t')[0]
        desc = tx.split('\t')[1]


        # fixed_date =


def sanity_check_date_overrides(basic_tx, date_overrides):
    """ Make sure date override lines look reasonable / corresponds to real txs"""

    date_overrides_keys = [l.rsplit("\t", 1)[0] for l in date_overrides]
    if not date_overrides_keys:
        raise Exception("No date overrides found")
    num_unique_keys = len(set(date_overrides_keys))
    if len(date_overrides_keys) != num_unique_keys:
        raise Exception("Duplicate keys in date overrides {} != {}"
                        .format(len(date_overrides_keys), num_unique_keys))

    basix_tx_set = set(basic_tx)
    for override_key in  date_overrides_keys:
        if override_key not in basix_tx_set:
            raise Exception("Override key doesn't match any tx: {}".format(override_key))

    for line in date_overrides:
        original_date = get_date_at_index(line, 0)
        override_date = get_date_at_index(line, -1)
        if original_date <= override_date:
            raise Exception("Line has an override date {} prior to the original date {}: {}"
                            .format(original_date, override_date, line))

    print "Passed date overrides sanity check"

def get_date_at_index(line, index):
    return datetime.datetime.strptime(line.split('\t')[index], '%m/%d/%Y')


if __name__ == "__main__":
    main()
