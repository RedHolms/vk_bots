import requests
from ._vkapi import VkAPI
from .exceptions import *

class LongPollManager(object):
    def __new__(cls): return cls

    class LongPollServer(object):
        def __init__(self, token: str, groupID: int, vkApiSession: VkAPI.ApiSession = None, wait: int = 25,
                    server: str = None, ts: int = None, key: str = None) -> None:
            
            self.token = token
            self.groupID = groupID
            if type(vkApiSession) != VkAPI.ApiSession:
                vkApiSession = VkAPI.ApiSession(token)
            self.vkApi = vkApiSession
            
            longpollSettings = self.vkApi.method.groups.getLongPollSettings(group_id=groupID)
            self._longpollSettings = longpollSettings

            if not bool(longpollSettings['is_enabled']):
                raise LongPollDisabled()
            
            self.enabledEvents = [event for event in longpollSettings['events'] if bool(event)]

            if server == None or ts == None or key == None:
                response = self.vkApi.method.groups.getLongPollServer(group_id=groupID)
                key = response['key']
                server = response['server']
                ts = int(response['ts'])

            self._key = key
            self._server = server
            self._ts = ts
            self._prevTs = self._ts
            self._wait = wait
        def getServer(self) -> str:
            return "{server}?act=a_check&key={key}&ts={ts}&wait={wait}".format(server=self._server, key=self._key, ts=self._ts, wait=self._wait)
        def update(self) -> list:
            response = requests.get(self.getServer())

            if response.status_code not in range(200, 299):
                raise ConnectionError(response)

            json = response.json()

            if 'failed' in json:
                if json['failed'] == 1:
                    self._ts = int(json['ts'])
                    return self.update()
                elif json['failed'] in range(2, 3):
                    raise LongPollInfoWasLost(json['failed'])
                else:
                    raise UnknownLongPollCycleError(json['failed'])
            
            self._updates = json['updates']
            self._prevTs = self._ts
            self._ts = int(json['ts'])

            self.eventsCount = self._ts - self._prevTs
            self.isNewEvents = self.eventsCount > 0

            self.events = self._updates[-self.eventsCount:]
            return self.events
