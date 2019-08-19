import requests
import rynly_api_utils as api

DEFAULT_PHONE_NUM = '971-222-9649'
FILE_PATH = "/Users/mirek/inspired_addresses.tsv"

# change `environ` to run on prod vs UAT
def main(environ=api.UAT):
    validated_addresses = []
    failed_addresses = []

    address_lines = get_addresses(FILE_PATH)
    for i, address_line in enumerate(address_lines):
        print "{}) Validating line {}".format(i + 1, address_line)
        validated_address = get_validated_address(environ, address_line, failed_addresses)
        if validated_address:
            validated_addresses.append(validated_address)

    num_lines = len(address_lines)
    num_valid = len(validated_addresses)
    print "\nChecked {} addresses".format(num_lines)
    print "{} errors".format(len(failed_addresses))
    print "{} suggestions".format(num_lines - num_valid - len(failed_addresses))
    print "{} validated".format(num_valid)

    print "\nFailed address lines:"
    for failed_address in failed_addresses:
        print failed_address


def get_validated_address(environ, address_line, error_addresses):
    """
    Validate the given address. If it passess validation, return the resulting "valid address" object.
    Otherwise print validation errors and return None
    """
    [company, name, address, city, state, zipcode] = address_line

    address_payload = {
        "company": company,
        "city": city,
        "contactName": name,
        "line1": address,
        "phone": DEFAULT_PHONE_NUM,
        "state": state,
        "zip": zipcode
    }

    validation_url = "{}/api/hub/validateAddress".format(api.get_url(environ))
    headers = api.get_headers(environ)
    cookies = api.get_cookies(environ)

    raw_response = requests.post(validation_url, json=address_payload, headers=headers, cookies=cookies)
    response = raw_response.json()

    if response["hasError"]:
        print "\tErrors: {}".format(response["errors"])
        error_addresses.append(address_line)
        return None

    data = raw_response.json()["data"]
    input_addr = data["validatedAddress"] # server's version of our original address
    recommended_addr = data["recommendedAddress"]

    if not recommended_addr: # we passed validation
        return input_addr

    for field in recommended_addr:
        # these don't show up in the recommended address response
        if field in ["phone", "company"]:
            continue

        if field not in input_addr:
            print "\tField '{}' missing in original address".format(field)
            continue

        if recommended_addr[field] != input_addr[field]:
            print "\tValue mismatch on field '{}'".format(field)
            print "\t\tgiven value = '{}'".format(input_addr[field])
            print "\t\trecommended value = '{}'".format(recommended_addr[field])

    return None


def get_addresses(file_path):
    """ Load the given tsv file. Ignore blank lines. """
    with open(file_path) as f:
        lines = []
        for line in f.read().splitlines():
            if not line.replace("\t", ""):
                continue
            lines.append(line.split("\t"))
        return lines


if __name__ == '__main__':
    main()
