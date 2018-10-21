# Take a file of vocab words, look up their ngram counts, and save the results to file
#
# Uses the ngram API at http://phrasefinder.io/api

import requests

INPUT_FILE_NAME = 'words.txt'
OUTPUT_FILE_NAME = 'usage_counts.txt'

def main():

    words = load_words()
    confirm_continue()

    # TODO: parallelize
    words_done = 0
    usage_counts = []
    for word in words:
        print "Qurying API ({}/{})".format(words_done + 1, len(words))
        resp = requests.get('https://api.phrasefinder.io/', {'corpus': 'eng-us', 'query': word})
        # to preview response: pprint(resp.json())

        word_results = resp.json()['phrases']

        # multiple results correspond to different cases, e.g. "word," "Word," and "WORD"
        usage_count = 0
        for word_result in word_results:
            usage_count += word_result['mc'] # "match count"

        usage_counts += [usage_count]
        print "Usage count for {}: {}".format(word, usage_count)
        words_done += 1

    write_usage_counts(usage_counts)
    print "Done"

def load_words():
    print "Loding words from '{}'".format(INPUT_FILE_NAME)
    with open(INPUT_FILE_NAME) as f:
        words = f.read().splitlines()
        print "Loaded {} words:".format(len(words))
        print '\n'.join(words)
        return words

def confirm_continue():
    reply = str(raw_input('Continue? (y/n): ')).lower().strip()
    if reply != 'y':
        print "You said '{}', quitting".format(reply)
        exit(0)

def write_usage_counts(usage_counts):
    print "Writing {} usage counts to '{}'".format(len(usage_counts), OUTPUT_FILE_NAME)
    with open(OUTPUT_FILE_NAME, 'w') as f:
        for usage_count in usage_counts:
            f.write(str(usage_count) + '\n')

if __name__ == "__main__":
    main()