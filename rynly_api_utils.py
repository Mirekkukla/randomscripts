# Enums representing production vs UAT
PROD = "PROD"
UAT = "UAT"

def get_url(environ):
    url = {
        UAT: "https://uatuser.rynly.com",
        PROD: "https://user.rynly.com"
    }
    return url[environ]

# Use 'uncurl' to get the appropriate headers and cookies
UAT_COOKIES = {
    "RynlyAccessToken": "%2BRjECzm8Xk9Y%2BboADaS4FZu2%2FBjR0aBZ9cT8cXRzW59Va5xOgJpXoI1G%2F8DxuRGg",
    "__stripe_mid": "0551dbea-62af-4c95-acd3-a5bb1c097ad6",
    "__stripe_sid": "ff07cf80-9261-46c1-ae32-0012c4290720",
    "_ga": "GA1.2.257506453.1559084098"
}

# CAREFUL! These are client-specific
PROD_COOKIES = {
    # ".AspNetCore.Antiforgery.w5W7x28NAIs": "CfDJ8AYKSQAAm3pGtzOiVKhozmD_2DNR--tZmUH0ZGyOqQNSQLMowH7KMKdYXLJbKPPo1fW25_9MZdDiTDYx6co8qiofeGgISsEC3CYy5sQbJurWWJOTZ4ajpKXk4Q1BzRsdN2jk8vhESdWWeKPTqajtp68",
    # "RynlyAccessToken": "L%2FzqcGuHqGRwdpE2m5CWUs4kjtbwwxEpaaV7X9l01viLfBtA%2BUA3dqN7Xqa8Wgio",
    # "__stripe_mid": "c433aa6e-cb01-4d8f-90ee-f1206ba70d82",
    # "__stripe_sid": "1d43d20f-7ab5-4de3-94cc-592f38c07ae7",
    # "_ga": "GA1.2.257506453.1559084098",
    # "ai_session": "lfNag|1565825036519|1565825047720.86",
    # "ai_user": "z8atJ|2019-07-18T20:05:12.315Z"
}

def get_cookies(environ):
    cookies = {
        UAT: UAT_COOKIES,
        PROD: PROD_COOKIES
    }
    return cookies[environ]

def get_headers(environ):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,cs;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": get_url(environ),
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
