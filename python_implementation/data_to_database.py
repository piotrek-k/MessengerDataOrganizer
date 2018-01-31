"""
Module extracting messages from facebook messenger
"""

import sys
from lxml import html
import data_to_db_additional_modules.database_configuration as ds
from typing import List
import datetime
import re
import os
import data_to_db_additional_modules.data_converting_tools as tools
import glob

def find_all_threads(path_to_folder):
    """Looks for all html files. Then sends them to load_and_save_data

    Arguments:
        path_to_folder {[type]} -- [description]
    """

    array_of_file_names = glob.glob(path_to_folder + '/*.html')
    print(len(array_of_file_names), " threads discovered")
    count_files = 1
    for file in array_of_file_names:
        print(count_files, "/", len(array_of_file_names), " (",file,")")
        load_and_save_data(file)
        count_files += 1
    print("Finished")


def load_and_save_data(source_path):
    # try to extract chatId from file name
    # chatId = -1
    # chatIdSearchResult = re.search(r'.+\\(\d+)\.html$', source_path)
    # try:
    #     chatId = int(chatIdSearchResult.group(1))
    # except AttributeError:
    #     # chat id not found
    #     chatId = -1
    # print("ChatId: ", chatId)

    HTML_CONTENT = tools.load_data(source_path)
    TREE = html.fromstring(HTML_CONTENT)

    THREAD = TREE.find_class('thread')[0]
    chat_name = THREAD.findall("h3")[0].text
    chatId = ds.createChat(chat_name)

    users_in_thread = [] # keep users names in memory. checking if they exists in db takes time

    all_p_objects = THREAD.xpath("./p[parent::div[@class='thread']]")
    p_objects_to_consider = []
    for p in all_p_objects:
        p_text = p.text
        if p_text is None:
            p_text = ""
        if len(p.xpath("img|video|audio"))>0 or "".join(p_text.split()) != "":
            p_objects_to_consider.append(p)

    # message content and details are placed alternately
    for details, content in zip(THREAD.find_class("message"), p_objects_to_consider):
        message_author_name = details.find_class("user")[0].text
        userId = tools.check_if_user_exists_return_id(message_author_name, users_in_thread)
        
        external_media_paths = []
        try:
            external_media_paths = content.xpath("./img/@src|./video/@src|./audio/@src")
        except:
            pass

        date_as_text = details.find_class("meta")[0].text
        date = tools.string_date_to_object_date_converter(date_as_text)
        message_text = content.text
        
        if len(external_media_paths) > 0:
            for media_file_path in external_media_paths:
                # print("tst", message_author_name, message_text, media_file_path)
                ds.createMessage_AddLater(message_text, userId, chatId, date, media_file_path)
        else:
            ds.createMessage_AddLater(message_text, userId, chatId, date, "")

    ds.addAllFromWaitingQueue()

def information_for_user():
    print("-----------------------")
    print("\n")
    print("Application loads all html files with messenger data and saves it to SQLite database on your computer.")
    print("Your data will be saved in '../appData/doNotSync/database.db' file. Previous database, if exists, will be deleted, so make a copy if you need it.")
    input("Press Enter to continue...")

# print(len(sys.argv))
if len(sys.argv) > 1:
    if sys.argv[1] == "--help":
        print("Type path to folder with html files with messages as argument")
    if sys.argv[1] is not None:
        # print(sys.argv[1])
        #information_for_user()
        # print("TYPED PATH",sys.argv[1])
        # ds.remove_previous_db()
        find_all_threads(sys.argv[1])
else:
    information_for_user()
    path = input('Enter a path to folder with fb messenger data: ')
    # print("TYPED PATH",path)
    # ds.remove_previous_db()
    find_all_threads(path)
