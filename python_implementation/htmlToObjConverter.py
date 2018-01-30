"""
Module extracting messages from facebook messenger
"""

from lxml import html
import dataSaver as ds
from typing import List
import datetime
import re
import os
import sys
import toolsForDataConverting as tools
import glob

def findAllThreads(path_to_folder):
    array_of_file_names = glob.glob(path_to_folder + '/*.html')
    print(len(array_of_file_names), " threads discovered")
    count_files = 1
    for file in array_of_file_names:
        print("Extracting from file ", count_files)
        loadAndSaveData(file)
        count_files += 1


def loadAndSaveData(source_path):
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

    # message content and details are placed alternately
    for details, content in zip(THREAD.find_class("message"), THREAD.findall("p")):
        message_author_name = details.find_class("user")[0].text
        userId = tools.check_if_user_exists_return_id(message_author_name, users_in_thread)
        #print(message_author_name)

        date_as_text = details.find_class("meta")[0].text
        date = tools.string_date_to_object_date_converter(date_as_text)

        #print(date)
        #print(content.text, "utf-8")

        ds.createMessage_AddLater(content.text, userId, chatId, date)

    ds.addAllFromWaitingQueue()

if sys.argv[1] == "--help":
    print("Type path to folder with html files with messages as argument")
if sys.argv[1] is not None:
    print(sys.argv[1])
    findAllThreads(sys.argv[1])