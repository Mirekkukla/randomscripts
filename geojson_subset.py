n = 0
with open("/Users/mirek/Desktop/canada_fsa_2016_census_001.pretty.geojson", "r") as f_read, open("/Users/mirek/Desktop/canada_fsa_2016_census_001_province_35_.pretty.geojson", "w") as f_write:
    for line in f_read:

        if "PRUID" in line:
            if "\"PRUID\": \"35\"" in line:
                n += 1
                print line
                exit(0)
                f_write.write(line)
            continue

        f_write.write(line)

print "Done, found {} codes".format(n)
