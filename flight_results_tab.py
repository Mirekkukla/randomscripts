
import webbrowser
import argparse


"""
Script to help you find the cheapest day to fly between two sets of cities.
Provide "from airport(s)", "to airport(s)", and "departure date" and we'll open a new
browser tab with google flights results for the given parameters.

Expected use: run multiple times with parameters passed in as command-line arguments,
where you simply change the "departure date" parameter in between executions.

Example:
python flight_results_tab.py -f "PRG,VIE" -t "SFO,SJC" -d "2018-09-13"
"""
def main():

    [from_airports, to_airports, departure_date] = get_flight_params()

    base_url = 'https://www.google.com/flights#flt='

    currency_param = ';c:USD'
    mystery_params = ';e:1;sd:1;t:f'
    one_way_pamams = ';tt:o'
    all_static_params = currency_param + mystery_params + one_way_pamams

    full_url = base_url + from_airports + '.' + to_airports + '.' + departure_date + all_static_params
    # EX: https://www.google.com/flights#flt=PRG,VIE.JRO.2018-09-28;c:USD;e:1;sd:1;t:f;tt:o

    webbrowser.open(full_url)

def get_flight_params():
    """
    Get "from airport(s)", "to airport(s)", and "departure date" info,
    either as command-line arguments or from a command-line prompt.
    Return an array of strings: [from_airports, to_airports, departure_date]
    Note that this method does NOT do any kind of format validation.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', help='from airport(s), ex: "PRG,VIE"')
    parser.add_argument('-t', action='store', help='to airport(s), ex: "SFO,SJC"')
    parser.add_argument('-d', action='store', help='departure_date, ex: "2018-09-13"')
    args = parser.parse_args()

    from_airports = args.f if args.f else raw_input('from airport(s), ex: "PRG,VIE": ')
    to_airports = args.t if args.t else raw_input('to airport(s), ex: "PRG,VIE": ')
    departure_date = args.d if args.d else raw_input('departure_date, ex: "2018-09-13": ')

    return [from_airports, to_airports, departure_date]

if __name__ == "__main__":
    main()
