"""
Script to help you find cheap stopover destination between two fixed dates / cities.

Example usage:
python flight_explorer.py -f "LAX" -t "PRG" -d "2019-01-13" -a "2019-01-18"

In the above example, you know you want to leave LAX on 1/13 and be in PRG on 1/18.
This leaves you a few days to stop somewhere in between, so you want to find a city X with
two cheap one-way tickets: (LAX -> X) on 1/13 and (X -> PRG) on 1/18

The idea is to "explore" all flights leaving LAX on 1/13 (tab 1), "explore" all flights leaving PRG (*)
on 1/18 (tab 3), and visually spot a city that cheap to fly to from both locations.

Once you have a candidate city, look up actual tickets from LAX -> X (tab 2) and X -> PRG (tab 4).

(*) Why does tab 3 involve exploring flights OUT of PRG, when what we really want is to fly INTO PRG?
Unfortunatly, google maps doesn't let you "explore" flights arriving TO a city. The idea here is that
cost of flying A -> B on a given date is a good provy for the cost of flying B -> A.
"""

import webbrowser
from flight_results_tab import get_flight_params
from flight_results_tab import get_full_url

def main():

    [from_airports, to_airports, departure_date, arrival_date] = get_flight_params(need_arrival_date=True)

    # EX: https://www.google.com/flights#flt=LAX..2019-01-13;c:USD;e:1;sd:1;tt:o;t:e
    from_explore_url = get_full_url(from_airports, "", departure_date, explore=True)
    # EX: https://www.google.com/flights#flt=LAX.PRG.2019-01-13;c:USD;e:1;sd:1;tt:o;t:f
    from_results_url = get_full_url(from_airports, from_airports, departure_date)
    to_explore_url = get_full_url(to_airports, "", arrival_date, explore=True)
    to_results_url = get_full_url(to_airports, to_airports, arrival_date)

    for url in [from_explore_url, from_results_url, to_explore_url, to_results_url]:
        webbrowser.open(url)
        # print url

if __name__ == "__main__":
    main()
