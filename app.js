var cheerio = require('cheerio');
var fs = require('fs');

fs.readFile('appData\\doNotSync\\messages.htm', 'utf8', function (err, data) {
    if (err) {
        return console.log(err);
    }
    //console.log(data);

    console.log("Html loaded to memory...");

    var $ = cheerio.load(data);

    this.allMessages = [];
    this.listOfChats = [];
    this.chatsFromHtml = [];
    this.allUsers = [];
    this.chatsToUsersTable = []; //index - user id, values - chats ids

    console.log("Html evaluated...");

    htmlToData($('body'), $, this);

    console.log("Data loaded to memory...");

    console.log("allMessages: ", this.allMessages.length);
    console.log("listOfChats: ", this.listOfChats.length);
    console.log("allUsers: ", this.allUsers.length);

    for (var c in this.listOfChats) {
        var chat = this.listOfChats[c];
        for (var m in chat.allMembers) {
            var member = chat.allMembers[m];
            for (var idInAllUsers in this.allUsers) {
                if (this.allUsers[idInAllUsers] == member) {
                    this.chatsToUsersTable[idInAllUsers] = mergeTwoArrays([chat.id], this.chatsToUsersTable[idInAllUsers]);
                }
            }
        }
    }

    var THAT = this;
    var stream = fs.createWriteStream("appData\\doNotSync\\messages.txt");
    stream.once('open', function (fd) {
        stream.write(
            "ID | " +
            "UserName | " +
            "DateAsNumber | " +
            "DateOfPosting | " +
            "Message | " +
            "ChatID \n"
        );
        for (var m in THAT.allMessages) {
            var message = THAT.allMessages[m];
            var dateOfPosting = message.dateTime.getDate() + "/" + (message.dateTime.getMonth()+1) + "/" + message.dateTime.getFullYear() + " " + message.dateTime.getHours() + ":" + message.dateTime.getMinutes();
            stream.write(
                message.id + "|" +
                message.userName.replace(/\|/g, "%") + "|" +
                message.dateTimeAsNumber + "|" +
                dateOfPosting + "|" +
                message.message.replace(/\s+/g, " ").replace(/(\r\n|\n|\r|\t)/gm, "").replace(/\|/g, "%") + "|" +
                message.chatId + "\n");
        }

        stream.end();
        console.log("Saving done");
    });

    var stream2 = fs.createWriteStream("appData\\doNotSync\\chats.txt");
    stream2.once('open', function (fd) {
        stream2.write(
            "ID | " +
            "Title \n"
        );
        for (var c in THAT.listOfChats) {
            var chat = THAT.listOfChats[c];
            stream2.write(
                (c+1) + "|" +
                chat.title.replace(/\s+/g, " ").replace(/(\r\n|\n|\r|\t)/gm, "").replace(/\|/g, "%") + "\n");
        }
        stream2.end();
    });

    var stream3 = fs.createWriteStream("appData\\doNotSync\\users.txt");
    stream3.once('open', function (fd) {
        stream3.write(
            "ID | " +
            "User \n"
        );
        for (var u in THAT.allUsers) {
            var user = THAT.allUsers[u];
            stream3.write(
                (u+1) + "|" +
                user.replace(/\|/g, "%") + "\n");
        }
        stream3.end();
    });

    var stream4 = fs.createWriteStream("appData\\doNotSync\\chatsUsers.txt");
    stream4.once('open', function (fd) {
        stream4.write(
            "UserId | " +
            "ChatId \n"
        );
        for (var ctu in THAT.chatsToUsersTable) {
            var chatsToUsers = THAT.chatsToUsersTable[ctu];
            for (var c in chatsToUsers) {
                stream4.write(
                    (ctu+1) + "|" +
                    chatsToUsers[c] + " \n");
            }
        }
        stream4.end();
    });
});

function htmlToData(elem, $, context) {
    //var elem = $(htmlObject.nativeElement); //kontener w który wczytano HTML z pliku
    var chatElems = elem.find(".contents div .thread"); //znajdź wszystkie obiekty .thread
    var countChats = 1; //zmienna do generowania ID
    var countMsgs = 1; //zmienna do generowania ID
    //var context = this; //zmienna pozwalająca na dostęp do zmiennych MessagesService
    chatElems.each(function () {
        var newChatData = {};
        newChatData.title = $(this).clone().children().remove().end().text();
        newChatData.id = countChats;
        newChatData.membersFromTitle = [];
        newChatData.membersGotFromMessages = [];
        newChatData.allMembers = [];
        var members = newChatData.title.split(",");
        for (var m in members) {
            newChatData.membersFromTitle.push(members[m].trim());
        }
        $(this).children().each(function () {
            var className = $(this).attr('class');
            var elementType = $(this).prop('tagName');
            var newMessageObject = {};

            if (className == "message") {
                var userName = $(this).find(".user").text();
                var dateTime = $(this).find(".meta").text();

                newMessageObject.userName = userName;
                newMessageObject.dateTimeAsText = dateTime;
                newMessageObject.chatId = newChatData.id;
                newMessageObject.dateTime = createDateTime(newMessageObject.dateTimeAsText);
                newMessageObject.dateTimeAsNumber = newMessageObject.dateTime.getTime();
                newMessageObject.id = countMsgs;

                var userIsInArray = false;
                for (var atm in newChatData.membersGotFromMessages) {
                    if (newChatData.membersGotFromMessages[atm] === userName) {
                        userIsInArray = true;
                        break;
                    }
                }
                if (!userIsInArray) {
                    newChatData.membersGotFromMessages.push(userName);
                }

                context.allMessages.push(newMessageObject);
                countMsgs++;
            }
            else if (elementType.toLowerCase().trim() == "P".toLowerCase().trim()) {
                var message = $(this).text();
                context.allMessages[context.allMessages.length - 1].message = message;
            }
        });

        newChatData.allMembers = mergeTwoArrays(newChatData.membersGotFromMessages, newChatData.membersFromTitle);

        //updating list of all users
        context.allUsers = mergeTwoArrays(context.allUsers, newChatData.allMembers);

        context.chatsFromHtml.push(newChatData);
        console.log("Chat ", countChats, "/", chatElems.length, " completed");
        countChats++;
    });

    mergeChats(context);
}

function mergeTwoArrays(a, b) {
    if (b == undefined) { b = []; }
    return a.concat(b.filter(function (item) {
        return a.indexOf(item) < 0;
    }));
}

function mergeChats(context) {
    var newAllChats = [];
    var idCounter = 1;
    for (var c in context.chatsFromHtml) {
        var chatExists = false;
        for (var n in newAllChats) {
            if (context.chatsFromHtml[c].title.trim().toLowerCase() === newAllChats[n].title.trim().toLowerCase()) {
                newAllChats[n].mergedFromThoseIds.push(context.chatsFromHtml[c].id);

                //łączenie tablic
                newAllChats[n].membersGotFromMessages = mergeTwoArrays(newAllChats[n].membersGotFromMessages, context.chatsFromHtml[c].membersGotFromMessages);
                newAllChats[n].allMembers = mergeTwoArrays(newAllChats[n].allMembers, context.chatsFromHtml[c].allMembers);

                chatExists = true;
                break;
            }
        }
        if (!chatExists) {
            var newChat = {};
            newChat.id = idCounter;
            newChat.title = context.chatsFromHtml[c].title;
            newChat.mergedFromThoseIds = [context.chatsFromHtml[c].id];
            newChat.membersFromTitle = context.chatsFromHtml[c].membersFromTitle;
            newChat.membersGotFromMessages = context.chatsFromHtml[c].membersGotFromMessages;
            newChat.allMembers = context.chatsFromHtml[c].allMembers;
            newAllChats.push(newChat);
            idCounter++;
        }
    }

    context.listOfChats = newAllChats;

    for (var a in context.allMessages) {
        var idChangeDone = false;
        var oldId = context.allMessages[a].chatId;
        for (var m in context.listOfChats) {
            for (var f in context.listOfChats[m].mergedFromThoseIds) {
                var checkid = context.listOfChats[m].mergedFromThoseIds[f];
                if (context.allMessages[a].chatId == checkid) {
                    context.allMessages[a].chatId = context.listOfChats[m].id;
                    idChangeDone = true;
                    break;
                }
            }
            if (idChangeDone) {
                break;
            }
        }

        if (context.listOfChats[context.allMessages[a].chatId - 1].title !== context.chatsFromHtml[oldId - 1].title) {
            console.error("Nowe chatid nie zgadza się z poprzednim");
            debugger;
        }
    }

    //zwalnianie pamięci
    context.chatsFromHtml = [];
}

function createDateTime(stringDate) {
    var reggie = /(\w*), (\w*) (\d*), (\d*) \w* (\d+):(\d{2})(\w*) (\w*\+\d{2})/;
    var dateArray = reggie.exec(stringDate);

    if (dateArray[7].toLowerCase().trim() == "pm".toLowerCase().trim()) {
        dateArray[5] = (parseInt(dateArray[5]) + 12) + "";
    }
    dateArray[1] = dateArray[1].substring(0, 3);
    dateArray[2] = dateArray[2].substring(0, 3);
    var dateFinalString = dateArray[1] + ", " + dateArray[3] + " " + dateArray[2] + " " + dateArray[4] + " " + (parseInt(dateArray[5]) - 1) + ":" + dateArray[6] + ":00 GMT";
    var dateOfMessage = new Date(Date.parse(dateFinalString));

    return dateOfMessage;
}