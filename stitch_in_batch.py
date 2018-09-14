from subprocess import call

# make sure all photos are in the script folder, and run the script from there

for n in range(1927, 1950, 2): # process images two at at time
    img_1 = "IMG_{}.JPG".format(n)
    img_2 = "IMG_{}.JPG".format(n+1)
    combined_img = "IMG_{}_{}.JPG".format(n, n+1)

    # images get stitched horizontally
    call(["convert", "+append", img_1, img_2, combined_img])

print "done"