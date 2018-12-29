"""
Script to help you find the cheapest day to fly between two sets of cities.
Provide "from airport(s)", "to airport(s)", and "departure date" and we'll open a new
browser tab with google flights results for the given parameters.

Expected use: run multiple times with parameters passed in as command-line arguments,
where you simply change the "departure date" parameter in between executions.

Example:
python flight_results_tab.py -f "PRG,VIE" -t "SFO,SJC" -d "2018-09-13"
"""

import webbrowser
import argparse

BASE_URL = 'https://www.google.com/flights#flt='

# ';c:USD' gives the currecy
# ';e:1;sd:1' are mystry params
# ';tt:o' indicates we're searching for one-ways
STATIC_PARAMS = ';c:USD;e:1;sd:1;tt:o'

def main():
    # Don't need the arrival date
    [from_airports, to_airports, departure_date, arrival_date] = get_flight_params()

    # EX: https://www.google.com/flights#flt=PRG,VIE.JRO.2018-09-28;c:USD;e:1;sd:1;tt:o;t:f
    full_url = get_full_url(from_airports, to_airports, departure_date)
    webbrowser.open(full_url)

def get_flight_params(need_arrival_date=False):
    """
    Get "from airport(s)", "to airport(s)", "departure date", and "arrival date" info,
    either as command-line arguments or from a command-line prompt. Arrival date is optional.
    Return an array of strings: [from_airports, to_airports, departure_date]
    Note that this method does NOT do any kind of format validation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', help='from airport(s), ex: "PRG,VIE"')
    parser.add_argument('-t', action='store', help='to airport(s), ex: "SFO,SJC"')
    parser.add_argument('-d', action='store', help='departure_date, ex: "2018-09-13"')
    parser.add_argument('-a', action='store', help='arrival_date, ex: "2018-09-31"')
    args = parser.parse_args()

    from_airports = args.f if args.f else raw_input('from airport(s), ex: "PRG,VIE": ')
    to_airports = args.t if args.t else raw_input('to airport(s), ex: "PRG,VIE": ')
    departure_date = args.d if args.d else raw_input('departure_date, ex: "2018-09-13": ')

    arrival_date = None
    if need_arrival_date:
        arrival_date = args.a if args.a else raw_input('arrival_date, ex: "2018-09-30": ')

    return [from_airports, to_airports, departure_date, arrival_date]

def get_full_url(from_airports, to_airports, date, explore=False):
    """
    Get the full google search URL corrsponding to the given params. If "to_airports" is given,
    you'll get flight results between the two cities. If "to_airports" is the empty string,
    you'll get the "exploring flights" map.
    """
    type_param = ";t:e" if explore  else ";t:f" # "exlore" mode or "flight list" mode
    return BASE_URL + from_airports + '.' + to_airports + '.' + date + STATIC_PARAMS + type_param

if __name__ == "__main__":
    main()
