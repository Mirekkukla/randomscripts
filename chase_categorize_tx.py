"""
Load a clean tsv file of chase tx lines, as exported by `chase_extract_tx.py`.
Try to categorize each transaction by examining the description.
- If we succeed, append a cell to the csv row with the category
- If not, leave the row unchanged

Export the resulting data as a new .tsv
"""

import os
import re

def main():

    base_folder = "/Users/mirek/temp/"
    filepath_to_read = os.path.abspath(base_folder + "mirek_2018_tx.tsv")
    filepath_to_write = os.path.abspath(base_folder + "mirek_2018_categorized_tx.tsv")

    lines = None
    with open(filepath_to_read) as f_read:
        lines = f_read.read().splitlines()


    for line in lines:

        if "brew" in line.lower():
            continue

        for coffee_term in ["costa", "starbucks", "philz", "java"]:
            if coffee_term in line.lower():
                continue

        for food_term in ["restaur", "sushi"]:
            if food_term in line.lower():
                continue



        if "coffee" in line.lower():
            print line

        # continue

        # print line


if __name__ == "__main__":
    main()
