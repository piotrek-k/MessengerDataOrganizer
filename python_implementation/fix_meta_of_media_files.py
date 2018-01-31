import data_to_db_additional_modules.database_configuration as dc
from peewee import *
import datetime
import os
import shutil
from pathlib import Path
import sys
import re

def to_two_char_string_with_leading_zero(number):
    if number <= 9 and number >= 0:
        return "0" + str(number)
    else:
        return str(number)

print("This app will restore metadata of images, videos and audio from messenger data")
print("You need to generate database using data_to_database.py first")

path_to_fb_data = ""
if len(sys.argv) > 1:
    path_to_fb_data = sys.argv[1]
else:
    path_to_fb_data = input("Type path to folder with facebook data. There should be 'messages' folder inside.")

print("Started...")

query = (dc.Message
            .select(dc.Message.external_media_path, dc.Message.date_utc, dc.Chat.name.alias("chatname"))
            .join(dc.Chat)
            .where(dc.Message.external_media_path != "")
            )

count = 0
number_of_fails = 0
for media in query:
    count+=1
    if count % 100 == 0:
        print(count, "/", len(query))

    path_from_db = media.external_media_path

    full_path = os.path.join(path_to_fb_data, path_from_db)
    file_extension = Path(full_path).suffix

    day = to_two_char_string_with_leading_zero(media.date_utc.day)
    month = to_two_char_string_with_leading_zero(media.date_utc.month)
    year = str(media.date_utc.year)
    hour = to_two_char_string_with_leading_zero(media.date_utc.hour)
    minute = to_two_char_string_with_leading_zero(media.date_utc.minute)

    new_filename = year + "-" + month + "-" + day + "-" + hour + "-" + minute + "" + file_extension
    new_file_directory = os.path.join(path_to_fb_data, "sorted_photos", re.sub('[^\w\-_\. ]', '_', media.posted_in.chatname))
    new_file_path = os.path.join(new_file_directory, new_filename)

    try: 
        os.makedirs(new_file_directory, exist_ok=True) # make sure destination folder exists
        shutil.copy2(full_path, new_file_path)
    except:
        number_of_fails+=1
        pass
print("Number of fails:",number_of_fails)







