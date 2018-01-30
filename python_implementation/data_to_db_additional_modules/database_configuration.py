"""
Configuring database, its shape and declaring possibly helpful functions to operate on it
"""

from peewee import *
from datetime import date
import os
import pytz
import datetime

PATH_TO_DB = "../appData/doNotSync/database.db"

def remove_previous_db():
    try:
        #input()
        os.remove(PATH_TO_DB)
    except OSError:
        pass

db = SqliteDatabase(PATH_TO_DB)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    name = CharField(unique=True)

class Chat(BaseModel):
    name = CharField(unique=True)

class Message(BaseModel):
    text = CharField(null = True)
    created_by = ForeignKeyField(User)
    posted_in = ForeignKeyField(Chat)
    date_with_timezone = DateTimeField()
    date_utc = DateTimeField()

def createChat(chatName):
    thread = Chat.get_or_create(name=chatName)
    return thread[0].id

def findChat(chatName):
    return (Chat.get(Chat.name == chatName))

def createUser(userName):
    return User.get_or_create(name = userName)

def createMessage(messageText, userId, chatId, dateOfPosting):
    utc_date = dateOfPosting.astimezone(pytz.utc)
    msg = Message.create(text=messageText, created_by = userId, posted_in = chatId, date_with_timezone=dateOfPosting, date_utc=utc_date)
    return msg.id

waiting_queue = []

def createMessage_AddLater(messageText, userId, chatId, dateOfPosting):
    utc_date = dateOfPosting.astimezone(pytz.utc)
    utc_date = utc_date.replace(tzinfo=None)
    waiting_queue.append({'text':messageText, 'created_by': userId, 'posted_in': chatId, 'date_with_timezone': dateOfPosting, 'date_utc':utc_date })
    if len(waiting_queue) >= 100: # default max in bulk insert is 999 https://www.sqlite.org/limits.html#max_variable_number
        addAllFromWaitingQueue()

def addAllFromWaitingQueue():
    if len(waiting_queue) == 0:
        return
    try:
        Message.insert_many(waiting_queue).execute()
    except:
        pass
    waiting_queue.clear()

db.connect()
db.create_tables([User, Chat, Message], True)
