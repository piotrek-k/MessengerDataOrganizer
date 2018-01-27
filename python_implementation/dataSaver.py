from peewee import *
from datetime import date

db = SqliteDatabase('../appData/messages.db')

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

db.connect()
db.create_tables([User, Chat, Message], True)

def createChat(chatName):
    thread = Chat.get_or_create(name=chatName)
    return thread[0].id

def findChat(chatName):
    return (Chat.get(Chat.name == chatName))

def createUser(userName):
    return User.get_or_create(name = userName)

def createMessage(messageText, userId, chatId):
    msg = Message.create(text=messageText, created_by = userId, posted_in = chatId, date=date.today())
    return msg.id
