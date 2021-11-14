import sys
import traceback

import requests

from ._vkapi import VkAPI
from .longpoll import LongPollManager
from . import utils, types, enums

class StopBot(Exception): pass

vk_bots = types.Empty()

class VKBots(object):
    """Main VKBots class"""
    def __new__(cls) -> None: return cls

    class UserSession(object):
        def __init__(self, user_id: int) -> None:
            self.id = user_id
            self.localData = types.Data()
        def setLocalData(self, **kwargs):
            for k, v in kwargs.items():
                self.localData[k] = v
        def getLocalData(self, key: str) -> types.typing.Any | None:
            """If value doesnt't exists then returns `None`"""
            key = str(key)
            if key not in self.localData:
                return None
            else:
                return self.localData[key]
    class Message(object):
        def __init__(self, messageID: int, vkApiSession: VkAPI.ApiSession,
                    sender_id: int = None, peer_id: int = None, messageObject: dict = None) -> None:
            self.id = messageID
            
            self.api = vkApiSession

            self.object = messageObject or self.api.methodRequest('messages.getById', {'message_ids': str(self.id)})
            if sender_id == None:
                sender_id = self.object['from_id']
            if peer_id == None:
                peer_id = self.object['peer_id']
            
            self.senderID = sender_id
            self.peerID = peer_id
        def _answer_to_message(self, text: str, 
            reply_to: int = None, forward_messages: list[int] = None, forward: dict = None,
            dont_parse_links: bool = False, disable_mentions: bool = False,
            random_id: int = 0) -> dict:
            """Return API Response of 'messages.send' method"""

            if not utils.only_one_of_values_not_equal(None, reply_to, forward_messages, forward):
                raise ValueError("Only one of params: [reply_to, forward_messages, forward] can be not 'None'")
            
            params = {
                "message": text,
                "random_id": random_id,
                "reply_to": reply_to,
                "forward_messages": forward_messages,
                "forward": forward,
                "dont_parse_links": int(dont_parse_links),
                "disable_mentions": int(disable_mentions),

                "peer_id": self.peerID
            }
            return self.api.methodRequest("messages.send", params)

        def Answer(self, text: str, *args, **kwargs):
            """`text = text.format(*args, **kwargs)`"""
            text = str(text).format(*args, **kwargs)

            reply_to = None

            if self.peerID > 2000000000:
                reply_to = self.id
            
            self._answer_to_message(text, reply_to=reply_to)

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
            for handler in self._handlers[self.HandlerType.CycleHandler]:
                self._call_handler(handler)

    # ===============================

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
        def onInvalidParams(self, messageObject: dict, receivedParams: list, expectedParams: list, invalidParamIndex: int): pass

        def onEvent_EVENT_PATH(self, eventObject: dict): pass
        def onCommand_COMMAND(self, messageObject: dict, params: list, userSession: vk_bots.VKBots.UserSession, messageClass: vk_bots.VKBots.Message): 
            """This method is just a hint about params of commands handlers"""
            pass

        # Methods initialization
        
        def onInit(self):
            self._commands: dict[str, dict] = {}
            #
            # Commands format:
            # {
            #   "CMD_NAME": types.Command()
            # }
            #
            self._users: dict[int, VKBots.UserSession] = {}
            self.SetCommandPrefix()

            def _onCycle(self: VKBots.Bot):
                # Updating longpoll server
                self.longpoll.update()

                for event in self.longpoll.events:
                    eventType = str(event['type'])
                    if self.Event._find_value_path(eventType) == None:
                        raise Exception("Handled unknown event: <%s>" % eventType)
                    eventObject = event['object']

                    handlerMethodName = "onEvent_" + str(self.Event._find_value_path(eventType))
                    if hasattr(self, handlerMethodName):
                        hndl = getattr(self, handlerMethodName)
                        self._call_handler(hndl, eventObject)
                    
                    if eventType in self._handlers[self.HandlerType.EventHandler]:                        
                        if eventType in self._handlers[self.HandlerType.EventHandler]:
                            handlers = self._handlers[self.HandlerType.EventHandler][eventType]
                            if type(handlers) == list:
                                for handler in handlers:
                                    if handler == hndl: continue
                                    self._call_handler(handler, eventObject)
                            else:
                                if handlers == hndl: continue
                                self._call_handler(handlers, eventObject)
                    continue
                return
            
            def _onEvent_Message_New(self: VKBots.Bot, eventObject: dict):
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

                    if cmdText in self._commands:
                        cmdObj = self._commands[cmdText]
                        cmdExpectedParams = cmdObj['params']
                        cmdParams, validParams, errorIndex = utils.check_params(cmdExpectedParams, cmdParams)
                        if not validParams:
                            # Calling on params error handlers
                            self.onInvalidParams(messageObject, cmdParams, cmdExpectedParams, errorIndex)
                            for handler in self._handlers[self.HandlerType.InvalidParamsHandler]:
                                self._call_handler(handler, messageObject, cmdParams, cmdExpectedParams, errorIndex)
                            return
                        
                        # Calling command handlers
                        if not messageSenderID in self._users:
                            userSession = VKBots.UserSession(messageSenderID)
                            self._users[messageSenderID] = userSession
                        else:
                            userSession = self._users[messageSenderID]
                        messageClass = VKBots.Message(messageID, self.api, messageSenderID, messagePeerID, messageObject)
                        
                        self._call_handler(cmdObj['handler'], messageObject, cmdParams, userSession, messageClass)
                return
            
            self.RegisterCycleHandler(_onCycle)
            self.RegisterEventHandler(self.Event.Message.New, _onEvent_Message_New)
            return
        pass