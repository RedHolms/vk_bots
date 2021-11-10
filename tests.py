from sys import argv
print(argv)

import vk_bots
from vk_bots import _vkapi as vk_api

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

class MainBot(vk_bots.VKBots.BotEmpty):
    def onInit(self):
        return super().onInit()
    pass

bot = MainBot(GROUP_ID, TOKEN)

print('\n')
print("Testing '_find_value_path' enums method")
print("===")
print('Event._find_value_path("wall_reply_new") = ', vk_bots.enums.Event._find_value_path("wall_reply_new"))
print("===")
