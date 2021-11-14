from sys import argv
print(argv)

import vk_bots
from vk_bots import _vkapi as vk_api
from json import dumps

_token = ''
_groupid = 0
_userid = 0
try:
    with open('tests_cfg.txt', 'rt', encoding='utf-8', newline='\n') as file:
        _lines = file.readlines()
        _token = _lines[0].strip('\r\n')
        _groupid = _lines[1].strip('\r\n')
        _userid = _lines[2].strip('\r\n')
except FileNotFoundError: 
    print("Warning: Tests Config File not found")
    pass

print("Tests config(token; groupID; userID)")
print("===")
print(_token)
print(_groupid)
print(_userid)
print("===")

TOKEN = _token 
GROUP_ID = _groupid
USER_ID = _userid

class MainBot(vk_bots.VKBots.Bot):
    def onEvent_Message_New(self, eventObject: dict):
        print("New message with text: " + str(eventObject['message']['text']))
    
    def onEvent_CallbackButton_Press(self, eventObject: dict):
        print("event_id=" + str(eventObject['event_id']))
        self.api.methodRequest("messages.sendMessageEventAnswer", 
        {
            'event_id': eventObject['event_id'], 
            'user_id': eventObject['user_id'], 
            'peer_id': eventObject['peer_id'], 
            'event_data': dumps({
                "type": "show_snackbar", 
                'text': 'Была нажата Callback кнопка!'
            })
        })
    
    def onInvalidParams(self, messageObject: dict, receivedParams: list, expectedParams: list, invalidParamIndex: int):
        print("Invalid params!")
        print("Message text: " + str(messageObject['text']))
        print("Expected params: " + str(expectedParams))
        print("Received params: " + str(receivedParams))
        print("Invalid param index: " + str(invalidParamIndex))
        print("===")

        self.api.methodRequest('messages.send', 
        {
            'peer_id': messageObject['peer_id'], 
            'random_id': 0, 
            'message': 'Параметры заданы не верно!'
        })
    
    def onCycle(self):
        return
    
    def onCommand_test(self, messageObject: dict, params: list, userSession: vk_bots.VKBots.UserSession, messageClass: vk_bots.VKBots.Message):
        print("User[ID:{0}] entered a command 'test'! Params: ".format(messageObject['from_id']) + str(params))
        if 'enter_count' not in userSession.localData:
            userSession.localData['enter_count'] = 0
        
        try:
            num = int(params[0])
        except:
            messageClass.Answer("Ожидается число!")
            return
        
        userSession.localData['enter_count'] += num
        messageClass.Answer("Счётчик: {0}".format(userSession.localData['enter_count']))

    
    def onInit(self):
        super().onInit()

        self.RegisterCommand("test", self.onCommand_test, 'Just test command', [vk_bots.types.CommandParam('Number', True, 1)])

        print(str(self._handlers))

        print("Bot was initialized!")

bot = MainBot(GROUP_ID, TOKEN)

bot.Start()