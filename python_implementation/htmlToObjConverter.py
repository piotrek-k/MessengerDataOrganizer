"""
Module extracting messages from facebook messenger
"""

from lxml import html
import dataSaver as ds
from typing import List
import datetime
import re

def load_data(filepath):
    """
    Function returning file content as string

    Args:
        filepath: path to messages.htm (file downloaded from facebook)
    """
    with open(filepath) as file:
        return file.read()

class User_with_db_id():
    """
    Object storing user name along with its database id
    """
    def __init__(self, name, db_id):
        self.name = name
        self.db_id = db_id

def users_to_database(array_of_names_users):
    """Gets all user names from provided array, check if they are present in database.
    Adds them to db if necessary.
    
    Arguments:
        array_of_names_users {string[]} -- list of names
    
    Returns:
        [type] -- [description]
    """

    array_of_users_with_db_id = []
    for user in array_of_names_users:
        in_db = ds.createUser(user)[0]
        array_of_users_with_db_id.append(User_with_db_id(user, in_db.id))
    return array_of_users_with_db_id

def check_if_user_exists_return_id(username, array_of_all_in_thread):
    """Check if name of user exsits in database, adds user to db if necessary
    
    Arguments:
        username {string} -- name of user
        array_of_all_in_thread {List[User_with_db_id]} -- list of object of type User_with_db_id
    """

    # speed up execution by iterating through local list of thread members
    for user in array_of_all_in_thread:
        if user.name == username:
            return user.db_id
    # no such user found, create new
    in_db = ds.createUser(username)[0]
    array_of_all_in_thread.append(User_with_db_id(in_db.name, in_db.id))
    return in_db.id

def string_date_to_object_date_converter(string_date):
    """Date from fb messenger looks like: Sunday, January 4, 2015 at 4:03pm UTC+01"""
    if re.match(".+\+\d\d$", string_date):
        # datetime converter needs timezone information as '+HHMM'. Facebook provides '+HH'
        # add zeros represeting minutes if necessary
        string_date += "00"
    return datetime.datetime.strptime(string_date, "%A, %B %d, %Y at %I:%M%p %Z%z")


HTML_CONTENT = load_data("../appData/template.html")
TREE = html.fromstring(HTML_CONTENT)

THREADS = TREE.find_class('thread')
for thread in THREADS:
    users_from_thread_name = [x.strip() for x in thread.text.split(',')]
    users_in_thread = users_to_database(users_from_thread_name)
    # print("THREAD NAME: ", thread_name)
    # print("USERS: ", users_in_thread)
    chatId = ds.createChat(thread.text.strip())

    for details, content in zip(thread.find_class("message"), thread.findall("p")):
        message_author_name = details.find_class("user")[0].text
        userId = check_if_user_exists_return_id(message_author_name, users_in_thread)
        print(message_author_name)

        date_as_text = details.find_class("meta")[0].text
        date = string_date_to_object_date_converter(date_as_text)

        print(date)