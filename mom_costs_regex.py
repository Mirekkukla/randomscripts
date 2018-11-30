import re

lines ="""-ATM Entebbe   $ 213.21 (Suzy 1/2)
-Hotel Victoria N1 first night $71.10  (Suzy 1/2)
-Hotel Tree Lodge at Sikumi $361.70 (Suzy 1/2)
-Hotel Safir Cairo $ 344.70 (Suzy 1/2)
-ATM Entebbe $ 221.90 (Suzy 1/2)
-Hotel Eco Inn Cairo $89.77 (Suzy 1/2)
-Hotel Victoria N1 last night N1 $ 71.10 (Suzy 1/2)
-Boba restaurant $62 (all Suzy-bracelets)
-Visa Egypt $ 50 (Suzy 1/2)
-ATM Kampala $221.90 (Suzy 1/2)
-ATM Cairo $224.08 (Suzy 1/2)
-ATM Cairo $168.06 (Suzy 1/2)
-ATM Cairo $112 (Suzy 1/2)
cash last day at Cairo $ 27.90 (all Suzy)
"""

for line in lines.splitlines():
    exp = r'[^$]+\$[ ]*([0-9\.]*)[ ]*(\(.*)'
    # print line
    regex_result = re.match(exp, line)
    # print regex_result.group(0) # print as much as will match
    amount_str = regex_result.group(1)
    desc = regex_result.group(2)
    print "{} {}".format(amount_str, desc)