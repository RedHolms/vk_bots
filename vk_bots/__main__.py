from ._vkapi import VkAPI
from .longpoll import LongPollManager

class VkBots(object):
    """Main VkBots class"""
    def __new__(cls) -> None: return cls

    class Bot(object):
        def __init__(self, token: str, groupID: int, longPollServer: LongPollManager.LongPollServer = None, vkApiSession: VkAPI.ApiSession = None) -> None:
            self.token = token
            self.groupID = groupID
            if type(vkApiSession) != VkAPI.ApiSession:
                vkApiSession = VkAPI.ApiSession(token)
            self.vkApi = vkApiSession

            if type(longPollServer) != LongPollManager.LongPollServer:
                longPollServer = LongPollManager.LongPollServer(token, groupID, self.vkApi)
            self.longpoll = longPollServer
    pass