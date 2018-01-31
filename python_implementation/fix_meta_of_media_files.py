import data_to_db_additional_modules.database_configuration as dc
from peewee import *
import datetime
import os
import shutil

def to_two_char_string_with_leading_zero(number):
    if number <= 9 and number >= 0:
        return "0" + str(number)
    else:
        return number

print("This app will restore metadata of images, videos and audio from messenger data")
print("You need to generate database using data_to_database.py first")

path_to_fb_data = input("Type path to folder with facebook data. There should be 'messages' folder inside.")

query = (dc.Message
            .select(dc.Message.external_media_path, dc.Message.date_utc, dc.Chat.name.alias("chatname"))
            .join(dc.Chat)
            .where(dc.Message.external_media_path != "")
            )

for media in query:
    path_from_db = media.external_media_path

    full_path = os.path.join(path_to_fb_data, path_from_db)
    path_without_extension, file_extension = os.path.splitext(full_path)

    day = to_two_char_string_with_leading_zero(media.date_utc.day)
    month = to_two_char_string_with_leading_zero(media.date_utc.month)
    year = media.date_utc.year
    hour = to_two_char_string_with_leading_zero(media.date_utc.hour)
    minute = to_two_char_string_with_leading_zero(media.date_utc.minute)

    new_filename = year + "-" + month + "-" + day + "-" + hour + "-" + minute + "." + file_extension
    new_filepath = os.path.join(path_to_fb_data, "sorted_photos", media.chatname, new_filename)

    shutil.copy2(full_path, new_filepath)







