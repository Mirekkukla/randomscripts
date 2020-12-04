n = 0
with open("/Users/mirek/Desktop/canada-forward-sortation-areas.geojson", "r") as f_read, open("/Users/mirek/Desktop/canada_ontario.geojson", "w") as f_write:
    for line in f_read:

        if "PRUID" in line:
            if "\"PRUID\": \"35\"" in line:
                n += 1
                f_write.write(line)
            continue

        f_write.write(line)

print "Done, found {} codes".format(n)
