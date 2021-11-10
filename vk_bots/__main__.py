import sys
import traceback
from types import FunctionType

import requests

import json

from ._vkapi import VkAPI
from .longpoll import LongPollManager
from . import utils, types, enums
import vk_bots


class StopBot(Exception): pass

class VKBots(object):
    """Main VKBots class"""
    def __new__(cls) -> None: return cls

    class HandlerType(enums.HandlerType): pass
    class Event(enums.Event): pass

    class BotEmpty(object):
        class HandlerType(enums.HandlerType): pass
        class Event(enums.Event): pass

        def __init__(self, groupID: int | str, accessToken: str, safeMode: bool = False,
                    httpSession: requests.Session = None, 
                    apiSession: VkAPI.ApiSession = None,
                    longPollServer: LongPollManager.LongPollServer = None) -> None:
            """
            Parameters
            ----------
            groupID : int
                ID of Group
            accessToken : str
                Group Acess Token
            safeMode : bool, optional
                If true errors will not stop bot working, by default `False`
            httpSession : requests.Session, optional
                HTTP Session from module `requests`, if `None` then standart session will be used, by default `None`
            apiSession : VkAPI.ApiSession, optional
                API Session from sub-module `_vkapi`, if `None` then API Session will be created by received token, by default `None`
            longPollServer : LongPollManager.LongPollServer, optional
                Long Poll Server from sub-module `longpoll`, if `None` then Long Poll Server will be created by received token and group ID, `wait` will be `30`, by default `None`
            """
                
            self.groupID = groupID
            self.token = accessToken

            if type(httpSession) != requests.Session:
                httpSession = requests.Session()
            self._http_session = httpSession

            if type(apiSession) != VkAPI.ApiSession:
                apiSession = VkAPI.ApiSession(token=self.token, httpSession=self._http_session)
            self.api = apiSession

            if type(longPollServer) != LongPollManager.LongPollServer:
                longPollServer = LongPollManager.LongPollServer(self.token, self.groupID, self.api, 30)
            self.longpoll = longPollServer

            self._handlers = {
                str(_handler_type) : 
                    dict() if str(_handler_type).endswith('$DICT') else 
                    list()
                    for _handler_type in self.HandlerType
            }

            self._bot_started = False

            self.safeMode = safeMode

            self.onInit()

        # Utils

        def _print_traceback(self):
            print("Traceback:")
            print("================")
            print(traceback.format_exc())
            print("================")
        
        # Handlers utils

        def _call_handler(self, handler: types.typing.Callable, *args, **kwargs):
            if not callable(handler):
                raise TypeError("Invalid type of param #1 'handler': Expected callable type")
            if type(handler) == types.MethodType:
                return handler(*args, **kwargs)
            else:
                return handler(self, *args, **kwargs)
        def _register_handler(self, handler_type: enums.HandlerType, handler: types.typing.Callable, name: str) -> None:
            handler_type = str(handler_type)
            name = str(name)

            if not callable(handler):
                raise TypeError("Invalid type of param #3 'handler': Expected callable type")
            
            if handler_type not in self.HandlerType:
                raise TypeError("Invalid type of param #1 'handler_type': Invalid handler type")
            
            handler_type_obj = self._handlers[handler_type]

            if type(handler_type_obj) == dict:
                if name in handler_type_obj:
                    if callable(handler_type_obj[name]):
                        _temp = handler_type_obj[name]
                        handler_type_obj[name] = [_temp, handler]
                    else:
                        handler_type_obj[name].append(handler)
                else:
                    handler_type_obj[name] = handler
            else:
                handler_type_obj.append(handler)
        def _unregister_handler(self, handler_type: enums.HandlerType, nameOrIndex: str | int, id: int = 0) -> None:
            handler_type = str(handler_type)

            if handler_type not in self.HandlerType:
                raise TypeError("Invalid type of param #1 'handler_type': Invalid handler type")
            
            handler_type_obj = self._handlers[handler_type]

            try:
                if nameOrIndex in handler_type_obj:
                    if type(handler_type_obj[nameOrIndex]) == list:
                        del handler_type_obj[nameOrIndex][id]
                    else:
                        del handler_type_obj[nameOrIndex]
            except: 
                print(f"Warning! Error raised while unregistering handler<{handler_type}> with name(or Index) '{nameOrIndex}'")
                self._print_traceback()
                print("It's not critical so bot will continue working")
                return
        
        # Handlers

        def RegisterCycleHandler(self, handler: types.typing.Callable) -> int:
            if not callable(handler):
                raise TypeError("Invalid type of param #1 'handler': Expected callable type")

            self._register_handler(self.HandlerType.CycleHandler, handler, '')
            return self._handlers[self.HandlerType.CycleHandler].__len__() - 1
        def UnregisterCycleHandler(self, index: int):
            self._unregister_handler(self.HandlerType.CycleHandler, index)

        # Methods

        def onInit(self):
            """Calls after bot initialization"""
            return
        def beforeIteration(self):
            """Calls every bot iteration before calling all handlers"""
            return
        def afterIteration(self):
            """Calls every bot iteration after calling all handlers"""
            return

        # Bot Cycle Methods

        def Start(self):
            self._bot_started = True
            self._cycle()
        def Stop(self):
            self._bot_started = False
        def HardStop(self):
            if self._bot_started == True:
                self._bot_started = False
                raise StopBot()

        def _cycle(self):
            while self._bot_started:
                try:
                    self.beforeIteration()
                    self._iteration()
                    self.afterIteration()
                except:
                    e = sys.exc_info()[0]
                    if e == StopBot:
                        print("\n")
                        print("Bot was hard stopped")
                        self._print_traceback()
                        print("Exiting from cycle...")
                        self.Stop()
                        return
                    else:
                        if self.safeMode:
                            print("\n")
                            print("Error was raised while bot working.")
                            self._print_traceback()
                            print("Bot will continue working")
                            print("_________________________")
                            continue
                        else:
                            print("\n")
                            print("Error was raised while bot cycle.")
                            self._print_traceback()
                            print("Exiting...")
                            raise SystemExit(1)
        def _iteration(self):
            for handler in self._handlers[self.HandlerType]:
                self._call_handler(handler)

    class Bot(BotEmpty):
        # Handlers

        def RegisterEventHandler(self, event: enums.Event, handler: types.typing.Callable) -> int:
            event = str(event)
            if event not in self.Event:
                raise TypeError("Invalid type of param #1 'event': Invalid event")
            if not callable(handler):
                raise TypeError("Invalid type of param #2 'handler': Expected callable type")
            
            self._register_handler(self.HandlerType.EventHandler, handler, event)
            _eventObj = self._handlers[self.HandlerType.EventHandler][event]
            return _eventObj.__len__() - 1 if type(_eventObj) == list else 0
        
        def UnregisterEventHandler(self, event: enums.Event, index: int = 0) -> None:
            event = str(event)
            if event not in self.Event:
                raise TypeError("Invalid type of param #1 'event': Invalid event")
            
            self._unregister_handler(self.HandlerType.EventHandler, event, index)


        def RegisterInvalidParamsHandler(self, handler: types.typing.Callable) -> int:
            if not callable(handler):
                raise TypeError("Invalid type of param #1 'handler': Expected callable type")

            self._register_handler(self.HandlerType.InvalidParamsHandler, handler, '')
            return self._handlers[self.HandlerType.InvalidParamsHandler].__len__() - 1
        
        def UnregisterInvalidParamsHandler(self, index: int):
            self._unregister_handler(self.HandlerType.InvalidParamsHandler, index)
        
        # Commands

        def RegisterCommand(self, command: str, handler: types.typing.Callable, about: str = '', params: list[types.CommandParam] = []):
            command = str(command)
            about = str(about)

            if not callable(handler):
                raise TypeError("Invalid type of param #2 'handler': Expected callable type")
            
            self._commands[command] = types.Command(command, handler, about, params)
        
        def UnregisterCommand(self, command: str) -> bool:
            """If returns `True` command was deleted, else error occured while deleting(in most times command doesn't exists)"""
            command = str(command)

            try:
                del self._commands[command]
                return True
            except:
                return False
        
        # Another

        def SetCommandPrefix(self, prefix: str = '/'):
            self.commandPrefix = str(prefix)
        
        # Methods declaration

        def onCycle(self): pass

        def onEvent_Message_New(self): pass

        # Methods initialization
        
        def onInit(self):
            self._commands = {}
            self.commandPrefix = self.SetCommandPrefix()

            def _onCycle(self: self):
                # Updating longpoll server
                self.longpoll.update()

                for event in self.longpoll.events:
                    eventType = event['type']
                    eventObject = event['object']

                    if eventType in self._handlers[self.HandlerType.EventHandler]:
                        handlers = self._handlers[self.HandlerType.EventHandler]
                        if type(handlers) == list:
                            for handler in handlers:
                                self._call_handler(handler, eventObject)
                        else:
                            self._call_handler(handlers, eventObject)
                    continue
                return
            
            def _onEvent_Message_New(self: self, eventObject: dict):
                messageObject = eventObject['message']
                messageID: int = messageObject['id']
                messageText: str = messageObject['text']
                messageSenderID: int = messageObject['from_id']
                messagePeerID: int = messageObject['peer_id']

                if messageText.startswith(self.commandPrefix):
                    # If message is command
                    woPrefix = messageText[len(self.commandPrefix):]
                    # woPrefix = With Out Prefix

                    splited = utils.split_msg_to_params(woPrefix)
                    cmdText = splited[0]
                    cmdParams = splited[1:]


                return
            return
        pass