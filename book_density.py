from collections import defaultdict
# Figure out how many books you'd have to review as a function of review schedule.
# - Assume you review N books every interval
# - After you reviewed a book for the first time, you review it 1 interval later
# - Then you review it 2 intervals later, then you review it 4 intervals later...
#
# Example:
# 20 books a year, review every six month (so 10 every interval), double that every time
# i0: t = 0: nothing
# i1: t = .5 year: 10 (t_0) = 10
# i2: t = 1 year: 10 (t_.5) = 10 [20]
# i3: t = 1.5 years: 10 (t_1) + 10 (t_0) = 20 [40]
# i4: t = 2 years: 10 (t_1.5)+ 10 (t_.5) = 20 [60]
# i5 t = 2.5 years: 10 (t_2) + 10 (t_1) = 20 [80]
# t = 3 years: 10 (t_2.5) + 10 (t_1.5) = 20 [100]
# t = 3.5 years: 10 (t_3) + 10 (t_2) + 10 (t_0)  = 30 [130]

reviews_by_interval = defaultdict(int)

def simulate(books_per_interval, number_of_intervals):

    for i in range(1, number_of_intervals + 1):
        reviews_by_interval[i] += books_per_interval

        additional_intervals = 2
        next_interval = i + additional_intervals

        while (next_interval <= number_of_intervals):
            reviews_by_interval[i] += books_per_interval
            additional_intervals = 2 * additional_intervals
            next_interval += additional_intervals

    print(reviews_by_interval)



def main():
    # N = 20 years, reivew every six months, double every time
    # 10 books per interval, 20 intervals

    simulate(10, 20)

if __name__ == "__main__":
    main()
