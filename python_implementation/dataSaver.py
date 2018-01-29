from peewee import *
from datetime import date
import os

os.remove("../appData/database.db")
db = SqliteDatabase("../appData/database.db")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    name = CharField(unique=True)

class Chat(BaseModel):
    name = CharField(unique=True)

class Message(BaseModel):
    text = CharField()
    created_by = ForeignKeyField(User)
    posted_in = ForeignKeyField(Chat)
    date = DateTimeField()

def createChat(chatName):
    thread = Chat.get_or_create(name=chatName)
    return thread[0].id

def findChat(chatName):
    return (Chat.get(Chat.name == chatName))

def createUser(userName):
    return User.get_or_create(name = userName)

def createMessage(messageText, userId, chatId, dateOfPosting):
    msg = Message.create(text=messageText, created_by = userId, posted_in = chatId, date=dateOfPosting)
    return msg.id

waiting_queue = []

def createMessage_AddLater(messageText, userId, chatId, dateOfPosting):
    waiting_queue.append({'text':messageText, 'created_by': userId, 'posted_in': chatId, 'date': dateOfPosting})

def addAllFromWaitingQueue():
    Message.insert_many(waiting_queue).execute()
    waiting_queue.clear()

db.connect()
db.create_tables([User, Chat, Message], True)
