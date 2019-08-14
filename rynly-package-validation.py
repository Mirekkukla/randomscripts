import json
import requests

VALIDATION_URL = 'https://uatuser.rynly.com/api/hub/validateAddress'
DEFAULT_PHONE_NUM = '971-708-6202'

def main():

    address_lines = get_addresses()
    num_validated = 0
    for address_line in address_lines:
        print "validating line {}".format(address_line)
        if validate_addressline(address_line):
            num_validated += 1

    print "Validated {} / {}".format(num_validated, len(address_lines))


def validate_addressline(address_line):
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
        "Origin": "https://uatuser.rynly.com",
        "Referer": "https://uatuser.rynly.com/user/Home/PackageCreate",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }

    cookies = {
        "RynlyAccessToken": "%2BRjECzm8Xk9Y%2BboADaS4FZu2%2FBjR0aBZ9cT8cXRzW59Va5xOgJpXoI1G%2F8DxuRGg",
        "__stripe_mid": "0551dbea-62af-4c95-acd3-a5bb1c097ad6",
        "__stripe_sid": "7b3dab1e-05f2-47ce-981f-ac56e5765989",
        "_ga": "GA1.2.257506453.1559084098"
        }

    raw_response = requests.post(VALIDATION_URL, json=orig_address, headers=headers, cookies=cookies)
    response = raw_response.json()

    if response["hasError"]:
        print "Errors"
        print response["errors"]
        print "\nFull response:"
        print json.dumps(raw_response.json(), indent=2)
        exit(1)

    data = raw_response.json()["data"]

    validated_addr = data["validatedAddress"] # validated version of our original address
    recommended_addr = data["recommendedAddress"]

    if not recommended_addr:
        return True

    else:
        print "Different address recommended"

        print "\nOriginal address:"
        print json.dumps(orig_address, indent=2)

        print "\nValidated address:"
        print json.dumps(validated_addr, indent=2)

        print "\nRecommended address"
        print json.dumps(recommended_addr, indent=2)

        print "\nMismatches:"
        for key, val in recommended_addr.iteritems():
            # these don't show up in the recommended address response
            if key in ["phone", "company"]:
                continue

            if key not in validated_addr:
                print "Key '" + key + "'' missing in original address"

            if recommended_addr[key] != validated_addr[key]:
                print "\nValue mismatch on key '{}'".format(key)
                print "(original address={})".format(validated_addr[key])
                print "validated addres={}".format(validated_addr[key])
                print "recommended addres={}".format(recommended_addr[key])

    return False


def get_addresses():
    filename = "/Users/mirek/inspired_addresses.tsv"
    with open(filename) as f:
        lines = []
        for line in f.read().splitlines():
            lines.append(line.split("\t"))
        return lines


if __name__ == '__main__':
    main()

# print "\nFull response:"
# print json.dumps(raw_response.json(), indent=2)
