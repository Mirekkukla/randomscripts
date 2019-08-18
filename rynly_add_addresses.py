import requests
import rynly_validate_addresses as val

# raw curl command:
# curl 'https://uatuser.rynly.com/api/user/saveAddress' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Origin: https://uatuser.rynly.com' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,cs;q=0.8' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36' -H 'Content-Type: application/json;charset=UTF-8' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://uatuser.rynly.com/user/Home/PackageCreate' -H 'Cookie: _ga=GA1.2.257506453.1559084098; __stripe_mid=0551dbea-62af-4c95-acd3-a5bb1c097ad6; RynlyAccessToken=%2BRjECzm8Xk9Y%2BboADaS4FZu2%2FBjR0aBZ9cT8cXRzW59Va5xOgJpXoI1G%2F8DxuRGg; __stripe_sid=7b3dab1e-05f2-47ce-981f-ac56e5765989' -H 'Connection: keep-alive' --data-binary '{"address":{"company":"Test","contactName":"Bro","line1":"1145 SE Spokane St","city":"Portland","state":"OR","zip":"97202","phone":"123-234-1234","location":{"latitude":45.465231,"longitude":-122.653967}}}' --compressed

# we replaced " with \" to uncurl

def main():

    validated_addresses = []

    address_lines = val.get_addresses()
    for i, line in enumerate(address_lines):

        [company, name, address, city, state, zipcode] = line
        print "{}) Uploading line {}".format(i + 1, line)

        validated_address = val.get_validated_address(line)
        print "Validated address: {}".format(validated_address)

        payload = {
            "address": {
                "company": company,
                "contactName": name,
                "line1": validated_address["line1"],
                "city": validated_address["city"],
                "state": validated_address["state"],
                "zip": validated_address["zip"],
                "phone": val.DEFAULT_PHONE_NUM,
                "location": validated_address["location"]
            }
        }

        print "Payload: {}".format(payload)

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


        response = requests.post("https://user.rynly.com/api/user/saveAddress", json=payload, headers=headers, cookies=cookies)

        print response
        print response.json()
        print "\n\n"

if __name__ == '__main__':
    main()
