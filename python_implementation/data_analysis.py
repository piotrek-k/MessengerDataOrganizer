import data_to_db_additional_modules.database_configuration as dc
from peewee import *

def string_change_size(text, size):
    if len(text) > size:
            text = text[:size]
    if len(text) < size:
            text = text.ljust(size)
    return text

def chats_time_range():
    print("chat name (chat id), date of first post (UTC), date of last post (UTC)")
    min_dates = (dc.Message
                    .select(dc.Message.posted_in, fn.MIN(dc.Message.date_utc).alias('mindate'), fn.MAX(dc.Message.date_utc).alias('maxdate'))
                    .group_by(dc.Message.posted_in)
                    .order_by(fn.MIN(dc.Message.date_utc)))
    for m in min_dates:
        formatted_name = m.posted_in.name.replace("Conversation with", "")
        print(string_change_size(formatted_name, 25), "(", m.posted_in.id  ,")", "\t", m.mindate, "\t", m.maxdate)

def count_all_messages():
    print("chat id \t chat name \t sum of all messages")
    message_count = fn.Count(dc.Message.id)
    query = (dc.Chat
             .select(dc.Chat.id, dc.Chat.name, message_count.alias('message_count'))
             .join(dc.Message)
             .group_by(dc.Chat.name)
             .order_by(message_count.desc()))
    
    for q in query:
        formatted_name = q.name.replace("Conversation with", "")
        formatted_name = string_change_size(formatted_name, 25)
        print(q.id, "\t", formatted_name, "\t", q.message_count)


def chat_by_month_activity(chatId):
    print("ChatID: ", chatId, " Name: ", dc.Chat.get(dc.Chat.id == chatId).name)

    month_column = dc.Message.date_utc.month
    year_column = dc.Message.date_utc.year
    message_count = fn.Count(dc.Message.id)
    yearmonth_column = year_column.concat("_").concat(month_column)
    query = (dc.Message
             # .select(dc.User.name, month_column.alias('month'), year_column.alias('year'), message_count.alias("messages_count"))
             .select(yearmonth_column.alias('yearmonth'), message_count.alias("messages_count"))
             .where(dc.Message.posted_in == chatId)
             .group_by(yearmonth_column)
             .order_by(message_count.desc())
             .order_by(month_column)
             .order_by(year_column)
             )
    # query = (dc.Message.select(dc.Message.date_utc.month).limit(5))

    for q in query:
        print(q.yearmonth, " ", q.messages_count, " ")


count_all_messages()
chats_time_range()
chat_by_month_activity(35)
