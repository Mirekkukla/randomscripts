import json
import requests
import rynly_api_utils as api
import rynly_validate_addresses as validation


def main(environ=api.UAT):
    validation_fails = []
    failed_payload_response_tuples = []
    address_lines = validation.get_addresses(validation.FILE_PATH)
    for i, line in enumerate(address_lines):

        #pylint: disable=unused-variable
        [company, name, address, city, state, zipcode] = line
        print "\n{}) Uploading line {}".format(i + 1, line)

        validated_address = validation.get_validated_address(environ, line, validation_fails)
        if not validated_address:
            print "Address failed validation, skipping"
            continue

        payload = {
            "address": {
                "company": company,
                "contactName": name,
                "line1": validated_address["line1"],
                "city": validated_address["city"],
                "state": validated_address["state"],
                "zip": validated_address["zip"],
                "phone": validation.DEFAULT_PHONE_NUM,
                "location": validated_address["location"]
            }
        }

        # print "Payload: {}".format(json.dumps(payload, indent=2))
        headers = api.get_headers(environ)
        cookies = api.get_cookies(environ)

        save_address_url = "{}/api/user/saveAddress".format(api.get_url(environ))
        response = requests.post(save_address_url, json=payload, headers=headers, cookies=cookies)

        print response
        if response.json()["hasError"]:
            print json.dumps(response.json(), indent=2)
            failed_payload_response_tuples.append((payload, response.json()))

    print "\n{} addresses failed validation:".format(len(validation_fails))
    for line in validation_fails:
        print line

    print "\n{} post request fails".format(len(failed_payload_response_tuples))
    for payload_resonse_tuple in failed_payload_response_tuples:
        print "Payload: {}".format(payload_resonse_tuple[0])
        print "\tResponse: {}".format(payload_resonse_tuple[1])

if __name__ == '__main__':
    main()
