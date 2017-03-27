import binascii
import os.path
import xml.etree.ElementTree as ET

# Take an xml export of your android SMS history using (some kind of) export tool
# Extract all of the underlying images

tree = ET.parse('sms-20160525233414.xml')
root = tree.getroot()
print "XML parsed"

message_count = 0
picture_count = 0

for message in root:
    # print "Message recieved on " + message.attrib['readable_date'] + " from " + message.attrib['contact_name'] + ": " + message.attrib['body']
    message_count += 1

    if message_count % 1000 == 0:
        print "{} messages processed".format(message_count)

    for message_section in message:
        if message_section.tag != "parts":
            continue

        for message_part in message_section:
            if message_part.attrib['ct'] != "image/jpeg":
                continue

            pic_str = message_part.attrib['data']
            pic_binary = binascii.a2b_base64(pic_str)

            # EX: "May 25, 2016 3:35:53 PM"
            raw_date = message.attrib['readable_date']
            sortable_date = raw_date.split(' ')[-3] + "_" + raw_date # just prefix the year

            image_file_name = sortable_date + ".jpeg"
            file_path = os.path.join("photos", image_file_name)
            with open(file_path, 'w') as f:
                f.write(pic_binary)
                picture_count += 1

print "Done, created {} pictures".format(picture_count)
