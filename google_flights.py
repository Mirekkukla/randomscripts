
import webbrowser

def main():
    # pull default airports from command line

    from_airports = raw_input('from airport(s), ex: "PRG,VIE"')
    # validate airports
    to_airports = raw_input('to airport(s), ex: "PRG,VIE"')
    departure_date = raw_input('departure_date, ex: "2018-09-13"')
    # validate date

    base_url = 'https://www.google.com/flights#flt='
    
    currency_param = ';c:USD'
    mystery_params = ';e:1;sd:1;t:f'
    one_way_pamams = ';tt:o'
    all_static_params = currency_param + mystery_params + one_way_pamams

    full_url = base_url + from_airports + '.' + to_airports + '.' + departure_date + all_static_params
    # EX: https://www.google.com/flights#flt=PRG,VIE.JRO.2018-09-28;c:USD;e:1;sd:1;t:f;tt:o


    webbrowser.open(full_url)
    # webbrowser.open(url[, new=0[, autoraise=True]])

    # print script call with parameters that would have done the current query

if __name__ == "__main__":
    main()