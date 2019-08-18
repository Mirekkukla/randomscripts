import json
import requests

VALIDATION_URL = 'https://user.rynly.com/api/hub/validateAddress'
DEFAULT_PHONE_NUM = '971-708-6202'
NUM_ERRORS = 0
ERRORS = []

def main():

    address_lines = get_addresses()
    validated_addresses = []
    num_validated = 0
    for i, address_line in enumerate(address_lines):
        print "{}) Validating line {}".format(i, address_line)
        validated_address = get_validated_address(address_line)
        validated_addresses.append(validated_address)

        if validated_address:
            num_validated += 1
        else:
            print ""

    num_lines = len(address_lines)
    print "Checked {} addresses".format(num_lines)
    print "{} errors".format(NUM_ERRORS)
    print "{} suggestions".format(num_lines - num_validated - NUM_ERRORS)
    print "{} validated".format(num_validated)

    print "ERRORS:"
    global ERRORS
    for error in ERRORS:
        print error


def get_validated_address(address_line):
    [company, name, address, city, state, zipcode] = address_line

    orig_address = {
        "company": company,
        "city": city,
        "contactName": name,
        "line1": address,
        "phone": DEFAULT_PHONE_NUM,
        "state": state,
        "zip": zipcode
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,cs;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://user.rynly.com",
        "Referer": "https://user.rynly.com/user/Home/PackageCreate",
        "Request-Context": "appId=cid-v1:b40138d5-f75d-4576-ba63-17f31d035d7e",
        "Request-Id": "|w3Jyg.Y3Qsn",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }

    cookies = {
        ".AspNetCore.Antiforgery.w5W7x28NAIs": "CfDJ8AYKSQAAm3pGtzOiVKhozmD_2DNR--tZmUH0ZGyOqQNSQLMowH7KMKdYXLJbKPPo1fW25_9MZdDiTDYx6co8qiofeGgISsEC3CYy5sQbJurWWJOTZ4ajpKXk4Q1BzRsdN2jk8vhESdWWeKPTqajtp68",
        "RynlyAccessToken": "L%2FzqcGuHqGRwdpE2m5CWUs4kjtbwwxEpaaV7X9l01viLfBtA%2BUA3dqN7Xqa8Wgio",
        "__stripe_mid": "c433aa6e-cb01-4d8f-90ee-f1206ba70d82",
        "__stripe_sid": "1d43d20f-7ab5-4de3-94cc-592f38c07ae7",
        "_ga": "GA1.2.257506453.1559084098",
        "ai_session": "lfNag|1565825036519|1565825047720.86",
        "ai_user": "z8atJ|2019-07-18T20:05:12.315Z"
    }

    raw_response = requests.post(VALIDATION_URL, json=orig_address, headers=headers, cookies=cookies)
    response = raw_response.json()

    # print "\nFull response:"
    # print json.dumps(raw_response.json(), indent=2)
    # exit(0)

    if response["hasError"]:
        print "Errors"
        print response["errors"]
        global NUM_ERRORS
        NUM_ERRORS += 1
        global ERRORS
        ERRORS.append(address_line)
        return None
        # print "\nFull response:"
        # print json.dumps(raw_response.json(), indent=2)
        # exit(1)

    data = raw_response.json()["data"]

    validated_addr = data["validatedAddress"] # validated version of our original address
    recommended_addr = data["recommendedAddress"]

    if not recommended_addr:
        return validated_addr

    else:
        print "Mismatches"

        # print "\nOriginal address:"
        # print json.dumps(orig_address, indent=2)

        # print "\nValidated address:"
        # print json.dumps(validated_addr, indent=2)

        # print "\nRecommended address"
        # print json.dumps(recommended_addr, indent=2)
        for key, val in recommended_addr.iteritems():
            # these don't show up in the recommended address response
            if key in ["phone", "company"]:
                continue

            if key not in validated_addr:
                print "Key '" + key + "'' missing in original address"

            if recommended_addr[key] != validated_addr[key]:
                print "Value mismatch on key '{}'".format(key)
                # print "(original address={})".format(validated_addr[key])
                print "\tvalidated addres={}".format(validated_addr[key])
                print "\trecommended addres={}".format(recommended_addr[key])

    return None


def get_addresses():
    filename = "/Users/mirek/inspired_addresses.tsv"
    with open(filename) as f:
        lines = []
        for line in f.read().splitlines():
            if not line.split("\t")[0]: # do less jank
                continue
            lines.append(line.split("\t"))
        return lines


if __name__ == '__main__':
    main()
