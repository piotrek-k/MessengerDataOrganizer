import unittest
import dataSaver

class DataSaverTest(unittest.TestCase):
    testChatName = "Chat testowy"
    testUserName = "Pietrek"
    testMessageContent = "Testowa wiadomosc"

    def test_tryCreatingChat(self):
        chatFound = dataSaver.createChat(self.testChatName)
        
        self.assertIsNotNone(chatFound)

    def test_tryCreatingUser(self):
        userFound = dataSaver.createUser(self.testUserName)

        self.assertIsNotNone(userFound)

    def test_createMessage_And_Connect_With_User_And_Chat(self):
        sampleChat = dataSaver.Chat.get(dataSaver.Chat.name == self.testChatName)
        sampleUser = dataSaver.User.get(dataSaver.User.name == self.testUserName)

        message = dataSaver.createMessage(self.testMessageContent, sampleUser.id, sampleChat.id)

        self.assertGreaterEqual(dataSaver.User.select().join(dataSaver.Message).where(dataSaver.Message.text == self.testMessageContent).count(), 1)