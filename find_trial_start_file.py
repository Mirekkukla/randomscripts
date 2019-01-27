"""
Script to find out where Radio Silence is storing its "trial started" data

Steps:
1. sudo opensnoop -n "Radio Silence" | unbuffer -p cut -d \/ -f2- > touched_files.txt
2. open radio silence and close it again
3. kill opensnoop command
4. uninstall Radio Silence
5. run this script

The script output will give you all files that were read by Radio Silence that still
exist after Radio Silence has been installed (we know the file containing trial data
info is one of these, since Radio Silence "knows" when your original trial started
even if you uninstall and re-install it).

"""

import os

IGNORE = ["CoreServices", "Google", "HMA", "Evernote"]

opensnoop_output_file = os.path.abspath("/Users/mirek/touched_files.txt")

def main():
    lines = []
    with open(opensnoop_output_file) as f:
        lines = f.read().splitlines()

    for line in lines:
        path_str = "/" + line[:-1]
        if not should_ignore(path_str):
            print path_str


# there's way too many files that get "touched" - we want to filter down to a subset
# that's likely to contain the Radio Sience specfic "trial started" data
def should_ignore(path_str):
    # happens to work for Radio Silence, might not for other apps though
    if "radio" not in path_str.lower():
        return True

    # safe for all apps
    if not os.path.exists(path_str) or not os.path.isfile(path_str):
        return True

    # probably safe for all apps
    for i in IGNORE:
        if i in path_str:
            return True

    return False


if __name__ == "__main__":
    main()
