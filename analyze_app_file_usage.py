"""
Script to help you explore which files are being modified by an application
Motivating example: find out where Radio Silence is storing its "trial started" data

Steps:
0. restart the computer (so that no pref values are cached)
1. sudo opensnoop > touched_files.txt
2. open radio silence, start trial, close it again
3. kill opensnoop command
4. uninstall radio silence
5. run this script

The script output will give you all files that were read by radio silence that still
exist after its been uninstalled (we know the file containing trial data
info is one of these, since Radio Silence "knows" when your original trial started
even if you uninstall and re-install it).

This script is meant to be used in an exploratory fashion
(see "START PLAYING WITH CODE HERE")
"""

import subprocess
import os

def main():
    opensnoop_output_file = os.path.abspath("/Users/mirek/touched_files.txt")
    with open(opensnoop_output_file) as f:
        lines = f.read().splitlines()

    paths = set()
    for line in lines:
        # example line: "     0  32688 xpcproxy       3 /dev/dtracehelper "
        # the path should start with the first occurance of "/"
        # one exception: modifications to the current directory (ie "."), which we can skip
        if "/" not in line:
            continue

        path_str = "/" + line.strip().split("/", 1)[1]

        # ignore folders / temp files that no longer exist
        if os.path.isfile(path_str):
            paths.add(path_str)

        # HACK: modifications to plist files don't get correctly reported
        # the reported filename has a temporary gibberish suffix
        # e.g. "/Users/mirek/Library/Preferences/com.radiosilenceapp.client.plist.eYVJgn5"
        if ".plist" in path_str and path_str.split(".plist", 1)[1]:
            fixed_plist_path = path_str.split(".plist")[0] + ".plist"
            if os.path.isfile(fixed_plist_path):
                paths.add(fixed_plist_path)

    print "Total existing files: {}".format(len(paths))

    # START PLAYING WITH CODE HERE
    # there's way too many files that get "touched" - we want to filter down to a subset
    # that's likely to contain the Radio Sience specfic "trial started" data
    # there are various filters we can play with; uncomment the one you want to run

    path_filtered_paths = print_paths_with_substring(paths, ["radiosilenceapp"]) # pass array w/ empty string to log all paths
    # basic_filtered_paths = run_basic_filter(paths)
    # grep_contents(path_filtered_paths, "trial")
    grep_plist_files(path_filtered_paths, "trial")
    # print_mirek_owned(basic_filtered_paths)


def print_paths_with_substring(paths, substring_list):
    """
    Find all paths that have EVERY string in the given `substring_list` as a substring.
    Comparisons are NOT case sensitive.
    """
    matched_paths = []
    for path in paths:
        all_match = True
        for substring in substring_list:
            if substring.lower() not in path.lower():
                all_match = False

        if all_match:
            print path
            matched_paths.append(path)

    print "Path substring search found: {}\n".format(len(matched_paths))
    return matched_paths


def grep_contents(paths, string_to_grep):
    """ Find all paths for which grep'ing for `string_to_grep` succeeds"""
    matched_paths = []
    for path in paths:
        grep_command = 'grep -i {} "{}"'.format(string_to_grep, path)

        # `os.system` doesn't let us capture the output, but that's ok - here we just want to print it
        # unlike `subprocess.check_output`, `os.system` doesn't throw exceptions on non-zero exit codes
        # which means it's faster (as well as simpler to use)
        exit_code = os.system(grep_command)
        if exit_code == 0:
            print path + "\n"
            matched_paths.append(path)

        # kept here for didactic purposes
        # try:
        #     grep_result = subprocess.check_output(grep_command, shell=True)
        #     print grep_result[:-1]
        #     matches += 1
        # except subprocess.CalledProcessError:
        #     pass

    print "Grep found: {}\n".format(len(matched_paths))
    return matched_paths


def grep_plist_files(paths, string_to_search):
    """ Read all plist files using "default" and grep the resulting text for `string_to_search`"""
    plist_paths = [path for path in paths if "plist" in path]
    matched_paths = []
    for path in plist_paths:
        grep_command = 'defaults read "{}" | grep -i "{}"'.format(path, string_to_search)
        exit_code = os.system(grep_command)
        if exit_code == 0:
            print path + "\n"
            matched_paths.append(path)

    print "Plist grep found: {}\n".format(len(matched_paths))
    return matched_paths


def print_mirek_owned(paths):
    """ Find all paths that are owned by user = mirek """
    matched_paths = []
    for path in paths:
        ls_info_raw = subprocess.check_output('ls -la "{}"'.format(path), shell=True)
        ls_info_line = ls_info_raw[:-1] # ditch newline
        if "mirek" in ls_info_line:
            print path
            matched_paths.append(path)

    print "mirek owned found: {}\n".format(len(matched_paths))
    return matched_paths


def run_basic_filter(paths):
    """ Remove all paths that likely have noting to do with our app (based on pathname) """

    # probably safe to ignore any file with one of these stings in the path
    # icudt59l.dat is unicode library related code
    def has_ignorable_keyword(inner_path_str):
        for keyword in ["CoreServices", "Google", "HMA", "Evernote", "Backup and Sync",
                        "Fonts", "iconservices", "Keyboard", "icudt59l.dat", "Carbon",
                        "timezone", "PkgInfo"]:
            if keyword in inner_path_str:
                return True
        return False

    matched_paths = []
    for path in paths:
        if has_ignorable_keyword(path):
            continue
        print path
        matched_paths.append(path)

    print "Basic filter found: {}\n".format(len(matched_paths))
    return matched_paths


if __name__ == "__main__":
    main()
