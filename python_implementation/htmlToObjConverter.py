"""
Module extracting messages from facebook messenger
"""

from lxml import html
import dataSaver as ds
from typing import List

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
    #return array_of_users_with_db_id

def check_if_user_exists(username, array_of_all_in_thread):
    """Check if name of user exsits in database, adds user to db if necessary
    
    Arguments:
        username {string} -- name of user
        array_of_all_in_thread {List[User_with_db_id]} -- list of object of type User_with_db_id
    """

    # speed up execution by iterating through local list of thread members
    for user in array_of_all_in_thread:
        if user.name == username:
            return
    # no such user found, create new
    in_db = ds.createUser(username)[0]
    array_of_all_in_thread.append(User_with_db_id(in_db.name, in_db.id))
    #return array_of_all_in_thread

HTML_CONTENT = load_data("../appData/template.html")
TREE = html.fromstring(HTML_CONTENT)

THREADS = TREE.find_class('thread')
for thread in THREADS:
    thread_name = thread.text.strip()
    users_from_thread_name = [x.strip() for x in thread_name.split(',')]
    print("THREAD NAME: ", thread_name)
    users_in_thread = users_to_database(users_from_thread_name)
    #print("USERS: ", users_in_thread)

    for details, content in zip(thread.find_class("message"), thread.findall("p")):
        message_author = details.find_class("user")[0].text
        check_if_user_exists(message_author, users_in_thread)
        print(message_author)

        print(details.find_class("meta")[0].text)
        print(content.text)
        print(" ")