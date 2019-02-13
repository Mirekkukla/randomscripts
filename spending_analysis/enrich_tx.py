"""
Load the single file of all aggregate tx
Enrich each tx with country information
and fix dates for flights and hotels
such that the "date" they're stamped with
is the date the expense is realized (ie flight
date / date of the hotel stay).

This helps us find out how much we're spending by
country / over time.

Date override format is the same as the normal tx
format, plus one more column at the end containing
the override date.

Country format: first column is the country, second
represents the "from" date - ie, the date we departed
for that country. Must be in chronological order
"""

import os
import datetime
import spending_utils as utils

folder_path = os.path.join(os.path.expanduser("~"), "final_spending")

basic_tx_path = os.path.join(folder_path, "all_tx.tsv")
enriched_tx_path = os.path.join(folder_path, "enriched_tx.tsv")

date_overrides_path = os.path.join(folder_path, "date_overrides.tsv")
countries_path = os.path.join(folder_path, "countries.tsv")


def main():
    basic_txs = utils.load_from_file(basic_tx_path)
    date_overrides = utils.load_from_file(date_overrides_path)
    sanity_check_date_overrides(basic_txs, date_overrides)

    country_lines = utils.load_from_file(countries_path)
    sanity_check_countries(country_lines)

    date_override_by_tx = {l.rsplit("\t", 1)[0] : l.split("\t")[-1] for l in date_overrides}

    enriched_txs = []
    for tx in basic_txs:

        fixed_date_str = tx.split('\t')[0]
        if tx in date_override_by_tx:
            fixed_date_str = date_override_by_tx[tx]
            print "Overriding {} with date {}".format(tx, fixed_date_str)

        country = get_country(country_lines, fixed_date_str)

        dateless_tx = tx.split("\t", 1)[1]
        enriched_tx = "{}\t{}\t{}".format(fixed_date_str, country, dateless_tx)
        enriched_txs.append(enriched_tx)

    utils.write_to_file(enriched_txs, enriched_tx_path)


def get_country(country_lines, tx_date_str):
    tx_date = get_date(tx_date_str)

    last_country = country_lines[0].split('\t')[0]
    for line in country_lines:
        country_from_date = get_date_at_index(line, 1)

        if country_from_date > tx_date:
            return last_country

        last_country = line.split('\t')[0]

    return last_country # tx occurs after the last listed country


#################### UTILS ####################


def get_date(date_str):
    return datetime.datetime.strptime(date_str, '%m/%d/%Y')


def get_date_at_index(line, index):
    return get_date(line.split('\t')[index])


#################### TESTS ####################


def sanity_check_countries(country_lines):
    """ Make sure date override lines look reasonable """

    if not country_lines:
        raise Exception("No country lines found")

    prior_date = None
    unique_countries = set()
    for line in country_lines:
        country = line.split('\t')[0]
        unique_countries.add(country)

        date = get_date_at_index(line, 1)
        if not prior_date:
            prior_date = date
            continue

        if not prior_date <= date:
            raise Exception("Prior date {} isn't < current date {} for {}".format(prior_date, date, country))

        prior_date = date

    print "Loaded {} unique contries:".format(len(unique_countries))
    print sorted(unique_countries)
    print "Pased country lines check"


def sanity_check_date_overrides(basic_txs, date_overrides):
    """ Make sure date override lines look reasonable / corresponds to real txs"""

    if not date_overrides:
        raise Exception("No date overrides found")

    date_overrides_keys = [l.rsplit("\t", 1)[0] for l in date_overrides]
    num_unique_keys = len(set(date_overrides_keys))
    if len(date_overrides_keys) != num_unique_keys:
        raise Exception("Duplicate keys in date overrides {} != {}"
                        .format(len(date_overrides_keys), num_unique_keys))

    utils.check_tsv_tx_format(date_overrides_keys, with_category=True)

    basix_tx_set = set(basic_txs)
    for override_key in date_overrides_keys:
        if override_key not in basix_tx_set:
            raise Exception("Override key doesn't match any tx: {}".format(override_key))

    for line in date_overrides:
        original_date = get_date_at_index(line, 0)
        override_date = get_date_at_index(line, -1)
        if override_date < original_date:

            # sometimes a hotel "charge" comes in after the "override date"
            # since the payment is made at the end of the stay
            date_diff = abs((original_date - override_date).days)
            if date_diff < 5:
                continue

            # cancelations come well after the override date
            if line.split('\t')[2][0] == "-":
                continue
            raise Exception("Line has an override date {} prior to the original date {}:\n{}"
                            .format(override_date, original_date, line))

    print "Passed date overrides sanity check"


def test_get_country():
    country_lines = ["FIRST\t12/15/2018", "SECOND\t01/31/2019", "THIRD\t12/01/2020"]

    def assert_true(date, expected_country):
        found_country = get_country(country_lines, date)
        if found_country != expected_country:
            raise Exception("For date {} expected {}, got country {}"
                            .format(date, expected_country, found_country))

    assert_true("12/15/2018", "FIRST")
    assert_true("12/16/2018", "FIRST")
    assert_true("01/30/2019", "FIRST")
    assert_true("01/31/2019", "SECOND")
    assert_true("02/01/2019", "SECOND")
    assert_true("12/01/2020", "THIRD")
    assert_true("12/02/2020", "THIRD")

    print "Passed 'test country' check"


if __name__ == "__main__":
    test_get_country()
    main()
