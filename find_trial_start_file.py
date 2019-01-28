#pylint: disable=anomalous-backslash-in-string
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
#pylint: enable=anomalous-backslash-in-string

import subprocess
import os

def main():
    opensnoop_output_file = os.path.abspath("/Users/mirek/touched_files.txt")
    with open(opensnoop_output_file) as f:
        lines = f.read().splitlines()

    paths = []
    for line in lines:
        path_str = "/" + line[:-1]
        # ignore folder and temp files that no longer exist
        if os.path.isfile(path_str) and os.path.exists(path_str):
            paths.append(path_str)

    # there's way too many files that get "touched" - we want to filter down to a subset
    # that's likely to contain the Radio Sience specfic "trial started" data
    # there are various filters we can play with; uncomment the one you want to run

    # basic_filtered_paths = run_basic_filter(paths)
    grep_contents(paths, "silence")
    # print_mirek_owned(basic_filtered_paths)


def grep_contents(paths, string_to_grep):
    matched_paths = []
    for path in paths:
        grep_command = 'grep -i {} "{}"'.format(string_to_grep, path)

        # `os.system` doesn't let us capture the output, but that's ok - here we just want to print it
        # unlike `subprocess.check_output`, `os.system` doesn't throw exceptions on non-zero exit codes
        # which means it's faster (as well as simpler to use)
        exit_code = os.system(grep_command)
        if exit_code == 0:
            matched_paths.append(path)

        # kept here for didactic purposes
        # try:
        #     grep_result = subprocess.check_output(grep_command, shell=True)
        #     print grep_result[:-1]
        #     matches += 1
        # except subprocess.CalledProcessError:
        #     pass

    print len(matched_paths)
    return matched_paths


def print_mirek_owned(paths):
    matched_paths = []
    for path in paths:
        ls_info_raw = subprocess.check_output('ls -la "{}"'.format(path), shell=True)
        ls_info_line = ls_info_raw[:-1] # ditch newline
        if "mirek" in ls_info_line:
            print path
            matched_paths.append(path)

    print len(matched_paths)
    return matched_paths


def run_basic_filter(paths):

    # probably safe to ignore any file with one of these stings in the path
    # icudt59l.dat is unicode library related code
    def has_ignorable_keyword(inner_path_str):
        for keyword in ["CoreServices", "Google", "HMA", "Evernote", "Backup and Sync",
                  "Fonts", "iconservices", "Keyboard", "icudt59l.dat", "Carbon", "timezone"]:
            if keyword in inner_path_str:
                return True
        return False

    matched_paths = []
    for path in paths:
        if has_ignorable_keyword(path):
            continue
        print path
        matched_paths.append(path)

    print len(matched_paths)
    return matched_paths


if __name__ == "__main__":
    main()
