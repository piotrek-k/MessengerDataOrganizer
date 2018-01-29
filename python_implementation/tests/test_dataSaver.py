import unittest
import dataSaver

class DataSaverTest(unittest.TestCase): 
    testChatName = "Chat testowy"
    testUserName = "Pietrek"
    testMessageContent = "Testowa wiadomosc"
    db = dataSaver

    def test_tryCreatingChat(self):
        chatFound = self.db.createChat(self.testChatName)
        
        self.assertIsNotNone(chatFound)

    def test_tryCreatingUser(self):
        userFound = self.db.createUser(self.testUserName)

        self.assertIsNotNone(userFound)

    def test_createMessage_And_Connect_With_User_And_Chat(self):
        sampleChat, chatWasCreated = self.db.Chat.get_or_create(name = self.testChatName)
        sampleUser, userWasCreated = self.db.User.get_or_create(name = self.testUserName)

        message = self.db.createMessage(self.testMessageContent, sampleUser.id, sampleChat.id)

        self.assertGreaterEqual(self.db.User.select().join(self.db.Message).where(self.db.Message.text == self.testMessageContent).count(), 1)