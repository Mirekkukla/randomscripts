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
import source_logic.spending_utils as utils

import source_logic.extract_chase_credit_tx as extract_chase_credit_tx
import source_logic.extract_chase_checking_tx as extract_chase_checking_tx
import source_logic.extract_schwab_checking_tx as extract_schwab_checking_tx

import source_logic.export_uncategorized_tx as export_uncategorized_tx
import source_logic.export_final_categorized_tx as export_final_categorized_tx

from source_logic.spending_utils import OperatingMode as OPMode

aggregate_tx_path = os.path.join(utils.get_aggregate_folder_path(), "aggregate_tx.tsv")
enriched_tx_path = os.path.join(utils.get_aggregate_folder_path(), "enriched_tx.tsv")

date_overrides_path = os.path.join(utils.get_aggregate_folder_path(), "date_overrides.tsv")
countries_path = os.path.join(utils.get_aggregate_folder_path(), "countries.tsv")


def main():

    extract_all_txs()
    export_all_uncategorized()

    aggregate_exported_txs()
    aggregate_txs = utils.load_from_file(aggregate_tx_path)

    date_overrides = utils.load_from_file(date_overrides_path)
    sanity_check_date_overrides(aggregate_txs, date_overrides)

    country_lines = utils.load_from_file(countries_path)
    sanity_check_countries(country_lines)

    date_override_by_tx = {l.rsplit("\t", 1)[0] : l.split("\t")[-1] for l in date_overrides}

    enriched_txs = []
    for tx in aggregate_txs:

        fixed_date_str = tx.split('\t')[0]
        if tx in date_override_by_tx:
            fixed_date_str = date_override_by_tx[tx]
            print "Overriding {} with date {}".format(tx, fixed_date_str)

        country = get_country(country_lines, fixed_date_str)

        dateless_tx = tx.split("\t", 1)[1]
        enriched_tx = "{}\t{}\t{}".format(fixed_date_str, country, dateless_tx)
        enriched_txs.append(enriched_tx)

    utils.write_to_file(enriched_txs, enriched_tx_path)


def extract_all_txs():
    """
    Run extraction logic for all sources
    """
    def exporter_fn():
        export_fn_by_mode = {
            OPMode.CHASE_CREDIT: extract_chase_credit_tx.main,
            OPMode.CHASE_CHECKING: extract_chase_checking_tx.main,
            OPMode.SCHWAB_CHECKING: extract_schwab_checking_tx.main
        }
        export_fn_by_mode[utils.OP_MODE]()

    run_for_all_op_modes(exporter_fn)


def export_all_uncategorized():
    """
    Exporting uncategorized tx for all modes. Quit at the first mode we encounter
    uncategorized tx at. If there are no uncategorized tx we simply proceed.
    """
    def export_uncategorized_fn():
        [uncategorized_lines, uncategorized_lines_filepath] = export_uncategorized_tx.main()
        if uncategorized_lines:
            print "Uncategorized lines for {}, see file at\n{}".format(utils.OP_MODE, uncategorized_lines_filepath)
            raise Exception("Uncategorized lines, see above")

    run_for_all_op_modes(export_uncategorized_fn)


def aggregate_exported_txs():
    """
    Create a single final with (un-enriched) categorized tx aggreagted across
    numerous operating modes.
    """
    all_lines = []
    def aggregator_closure_fn():
        all_lines.extend(export_final_categorized_tx.get_final_lines())

    run_for_all_op_modes(aggregator_closure_fn)
    print "Loaded all {} lines".format(len(all_lines))
    utils.write_to_file(all_lines, aggregate_tx_path)


def run_for_all_op_modes(fn):
    old_op_mode = utils.OP_MODE
    for op_mode in [OPMode.CHASE_CREDIT, OPMode.CHASE_CHECKING, OPMode.SCHWAB_CHECKING]:
        # HACK: global vars are evil
        print "HACK: former OP_MODE value was {}, changing to {}".format(utils.OP_MODE, op_mode)
        utils.OP_MODE = op_mode
        fn()
    print "HACK: return OP_MODE to {}".format(old_op_mode)
    utils.OP_MODE = old_op_mode


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
    print "Passed country lines check"


def sanity_check_date_overrides(basic_txs, date_overrides):
    """ Make sure date override lines look reasonable / corresponds to real txs"""

    if not date_overrides:
        raise Exception("No date overrides found")

    date_overrides_keys = [l.rsplit("\t", 1)[0] for l in date_overrides]
    num_unique_keys = len(set(date_overrides_keys))
    if len(date_overrides_keys) != num_unique_keys:
        print "Dupe key(s):"
        print set([x for x in date_overrides_keys if date_overrides_keys.count(x) > 1])
        raise Exception("Duplicate keys in date overrides {} != {}"
                        .format(len(date_overrides_keys), num_unique_keys))

    utils.check_tsv_tx_format(date_overrides_keys, with_category=True)

    basix_tx_set = set(basic_txs)
    for override_key in date_overrides_keys:
        if override_key not in basix_tx_set:
            raise Exception("Date override key doesn't match any tx: {}".format(override_key))

    for line in date_overrides:
        original_date = get_date_at_index(line, 0)
        override_date = get_date_at_index(line, -1)
        if override_date < original_date:

            # sometimes a hotel "charge" comes in after the "override date"
            # since the payment is made at the end of the stay
            date_diff = abs((original_date - override_date).days)
            if date_diff < 5:
                continue

            # cancelations and venmoish payments come well after the override date
            # can't just check "category" b/c some venmoish payments gets re-categorized as activities etc
            is_venmoish = any(s in line for s in ["VENMO", "SQC", "Zelle"])
            if line.split('\t')[2][0] == "-" or is_venmoish:
                continue
            raise Exception("Line has an override date {} prior to the original date {}:\n{}"
                            .format(override_date, original_date, line))

    # make sure all flights, hotels, and large venmoish txs have a date overrides entry
    date_overrides_set = set(date_overrides_keys)
    missing_overrides_entries = []
    for line in basic_txs:
        category = line.split("\t")[-1]
        amt = float(line.split("\t")[2].replace(",", ""))
        is_large_sqr = category == "SQR" and amt > 100
        if category != "F" and category != "H" and not is_large_sqr:
            continue

        if line not in date_overrides_set:
            missing_overrides_entries.append(line)

    missing_entries_path = os.path.join(utils.get_aggregate_folder_path(), "missing_date_entries.tsv")
    if missing_overrides_entries:
        utils.write_to_file(missing_overrides_entries, missing_entries_path)
        raise Exception("Some flight / hotel / large SQR tx doesn't have an date override entry, see above")

    if os.path.exists(missing_entries_path):
        print "Nuking existing 'missing override entries' file at {}".format(missing_entries_path)
        os.remove(missing_entries_path)

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
