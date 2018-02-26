import data_to_db_additional_modules.database_configuration as dc
from peewee import *
import sys
import inspect
import io
import matplotlib.pyplot as plt
import numpy as np

def string_change_size(text, size):
    if len(text) > size:
            text = text[:size]
    if len(text) < size:
            text = text.ljust(size)
    return text

def leading_zero(number):
    as_int = int(number)
    result = ""
    if(as_int <= 9 and as_int >= 0):
        result = "0" + str(as_int)
    else:
        result = "" + str(as_int)
    return result

def print_to_file(*arg):
    caller_function_name = inspect.stack()[1][3]
    with io.open('../appData/doNotSync/'+caller_function_name+'.csv', 'a', encoding='utf8') as f:
        for a in arg:
            f.write(str(a).replace(",", "[comma]") + ",")
        f.write("\n")

def clean_file():
    caller_function_name = inspect.stack()[1][3]
    open('../appData/doNotSync/'+caller_function_name+'.csv', 'w').close()

def chats_time_range():
    clean_file()
    print("chat name (chat id), date of first post (UTC), date of last post (UTC)")
    print_to_file("chat name", "chatId", "date of first post (UTC)", "date of last post (UTC)")
    min_dates = (dc.Message
                    .select(dc.Message.posted_in, fn.MIN(dc.Message.date_utc).alias('mindate'), fn.MAX(dc.Message.date_utc).alias('maxdate'))
                    .group_by(dc.Message.posted_in)
                    .order_by(fn.MIN(dc.Message.date_utc)))
    for m in min_dates:
        formatted_name = m.posted_in.name.replace("Conversation with", "")
        print(string_change_size(formatted_name, 25), "(", m.posted_in.id  ,")", "\t", m.mindate, "\t", m.maxdate)
        print_to_file(m.posted_in.name, m.posted_in.id, m.mindate, m.maxdate)

def count_all_messages():
    clean_file()
    print("chat id \t chat name \t sum of all messages")
    print_to_file("chatId", "chatName", "Sum of all messages")
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
        print_to_file(q.id, q.name, q.message_count)


def chat_by_month_activity(chatId):
    clean_file()
    print("ChatID: ", chatId, " Name: ", dc.Chat.get(dc.Chat.id == chatId).name)
    print_to_file("year_month", "sum of messages in specified time period", "year", "month")

    month_column = dc.Message.date_utc.month
    year_column = dc.Message.date_utc.year
    message_count = fn.Count(dc.Message.id)
    yearmonth_column = year_column.concat("_").concat(month_column)
    query = (dc.Message
             .select(yearmonth_column.alias('yearmonth'), message_count.alias("messages_count"), year_column.alias("year"), month_column.alias("month"))
             .where(dc.Message.posted_in == chatId)
             .group_by(yearmonth_column)
             .order_by(message_count.desc())
             .order_by(month_column)
             .order_by(year_column)
             )

    for q in query:
        print(q.yearmonth, " ", q.messages_count, " ")
        print_to_file(q.yearmonth, q.messages_count, q.year, q.month)

def assign_id_to_values(array, new_val):
    for a in array:
        if a[0] == new_val:
            return a[1]
    array.append([new_val, len(array)])
    return len(array)-1

def user_in_chat_by_month_activity(chatId):
    clean_file()
    print("ChatID: ", chatId, " Name: ", dc.Chat.get(dc.Chat.id == chatId).name)
    print_to_file("year_month_name", "name", "sum of messages in specified time period", "year", "month")
    
    month_column = dc.Message.date_utc.month
    year_column = dc.Message.date_utc.year
    message_count = fn.Count(dc.Message.id)
    yearmonthname_column = year_column.concat("_").concat(month_column).concat("_").concat(dc.User.name)
    yearmonth_column = year_column.concat("_").concat(month_column)
    query = (dc.Message
             .select(yearmonthname_column.alias('yearmonthname'),
                yearmonth_column.alias('yearmonth'),
                dc.User.name,
                dc.Message.date_utc,
                message_count.alias("messages_count"),
                year_column.alias("year"),
                month_column.alias("month"))
             .join(dc.User)
             .where(dc.Message.posted_in == chatId)
             .order_by(message_count.desc())
             .order_by(dc.Message.date_utc)
             .group_by(yearmonthname_column)
             
             #.order_by(month_column.cast('Integer'))
             #.order_by(year_column)
             
             )
    print(query.sql())

    participants = (dc.Message
                    .select(dc.Message.posted_in,
                        dc.User.name)
                    .join(dc.User)
                    .where(dc.Message.posted_in == chatId)
                    .group_by(dc.User.name))
    #print(participants.sql())
    all_year_months = (dc.Message.select(yearmonth_column.alias('yearmonth')).where(dc.Message.posted_in == chatId).group_by(yearmonth_column))

    # for p in time_ids:
    #     print(p.yearmonthname)
    all_year_months_as_string = []
    for ym in all_year_months:
        all_year_months_as_string.append(ym.yearmonth)
    yearmonths_and_id = []
    for p in participants:
        values = []
        data_for_one_user = query.where(dc.User.name == p.created_by.name)
        for ym in all_year_months:
            values_query = query.where((dc.User.name == p.created_by.name) & (ym.yearmonth == yearmonth_column) )
            if len(values_query) == 1:
                values.append(values_query[0].messages_count)
            elif len(values_query) > 1:
                values.append(-1)
            else:
                values.append(0)
        print(values)
        plt.plot(values, label=p.created_by.name)
        plt.xticks(np.arange(len(values)), all_year_months_as_string)
        #for d in data_for_one_user:
            #values.append()
            #print(d.created_by.name, d.messages_count, assign_id_to_values(yearmonths_and_id, d.yearmonth), "("+d.yearmonth+")")
    plt.xlabel('Month', fontsize=18)
    plt.ylabel('Messages', fontsize=16)
    plt.legend(loc='best')
    plt.xticks(fontsize=7, rotation=90)
    plt.show()

    # chart_data = []
    for q in query:
    #     chart_data.append([q.created_by.name, q.messages_count, str(q.year) + "_" + leading_zero(q.month)])
        print(q.yearmonthname, q.created_by.name, " ", q.messages_count, " ")
    #     print_to_file(q.yearmonthname, q.created_by.name, q.messages_count, q.year, q.month)
        # for x in query.where()
    # print(chart_data)
    # chart_data.sort(key=lambda x:x[2])
    # print("Sorted:")
    # print(chart_data)

    # plt.plot([row[1] for row in chart_data], [row[1] for row in chart_data])
    #plt.show()

all_options = [
    count_all_messages,
    chats_time_range,
    chat_by_month_activity,
    user_in_chat_by_month_activity
]

if len(sys.argv) > 1:
    for ao in all_options:
        if ao.__name__ == sys.argv[1]:
            if len(sys.argv) > 2:
                ao(sys.argv[2])
            else:
                ao()
else:
    print("--List of all options you can use:--")
    print("schema: [OPTION NAME] ([PARAMETERS IT TAKE]): ")
    print()
    for ao in all_options:
        print("\t", ao.__name__, "(",  list(inspect.signature(ao).parameters.keys()), ")")
            
