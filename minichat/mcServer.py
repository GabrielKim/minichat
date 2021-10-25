#-*- coding: utf-8 -*-

import asyncio
from typing import AsyncIterable

import threading
import time

# from concurrent import futures

import grpc

import minichat_pb2
import minichat_pb2_grpc

from etc.LRUDict import LRUDictforNumCheck # for user management

class mcServer(object):
    class mcServerServicer(minichat_pb2_grpc.mcServerServicerServicer):
        # mcServerServicer Class Area
        def __init__(self) -> None:
            self._connCloseTime = 2.0 # minutes

            self._chatLog = []
            self._userList = []
            self._chanList = {} # dict

            self._nowTime = 0
            self._connQuit = False

            threading.Thread(target=self._timerThread, daemon=True).start()

            self._lrudict = LRUDictforNumCheck(50)

        # Private Functions
        def _removeUserbyUserList(self, user: str) -> None:
            self._userList.remove(user)

        def _removeUserbyChanList(self, user: str, chan: str) -> bool:
            if chan in self._chanList.keys():
                if user in self._chanList[chan]:
                    self._chanList[chan].remove(user)
                    return True
            return False

        def _checkUserConn(self) -> None:
            for _user in self._userList:
                _dict = self._lrudict.front()
                if _user in _dict:
                    _useruptime = _dict[_user]
                    if _useruptime > 0 and (self._nowTime - _useruptime) > 60 * self._connCloseTime:
                        print("The connection was terminated by user \"{}\" for more than {} seconds. {}".format(_user, 60 * self._connCloseTime, (self._nowTime - _useruptime)))
                        # If the user has not do anything for 2 minutes..
                        # delete a user and channel connection list in user
                        
                        # delete user by LRU Dict
                        self._lrudict.delete(_user)
                        # delete user by user list
                        self._removeUserbyUserList(_user)
                        # delete user by channel list
                        for _chan in self._chanList:
                            if _user in self._chanList[_chan]:
                                self._chanList[_chan].remove(_user)
                                break
                        break

        def _findUserInChannel(self, user: str, channel: str) -> bool:
            if user in self._userList:
                # print("channel:{}".format(channel))
                # print("userlist:{}".format(self._userList))
                # print("chanlist:{}".format(self._chanList))
                # print("channel:{}, chanlist:{}".format(channel, self._chanList[channel]))
                if user in self._chanList[channel]:
                    return True
            return False

        # Threads
        def _timerThread(self) -> None:
            while not self._connQuit:
                time.sleep(1) 
                self._nowTime = time.time()
                self._checkUserConn()

        # gRPC Service Functions
        async def MessageStream(
            self, request: minichat_pb2.Req_User,
            unused_context) -> AsyncIterable[minichat_pb2.Resp_MessageToClient]:
            _index = 0

            # Grab the connection and send it to all
            while request.id in self._userList:
                while len(self._chatLog) > _index:
                    _chat = self._chatLog[_index]
                    _index += 1
                    # print("_chat[0]:{} _chat[1]:{} id:{} request.focusChan:{}".format(_chat[0], _chat[1], request.id, request.focusChan))
                    if _chat[0] == 'a' \
                        or (_chat[0] == 'g' and _chat[1] == request.focusChan):
                        yield minichat_pb2.Resp_MessageToClient(
                            "[" + _chat[2] + "]-> " + _chat[3])

        async def CommandStream(
            self, request: minichat_pb2.Req_MessageToServer,
            unused_context) -> AsyncIterable[minichat_pb2.Resp_MessageToClient]:
            _messages = []

            if request.command == 1:
                # for Save information on first connection(no operation)
                self._userList.append(request.id)
                self._lrudict.push(request.id, self._nowTime)
                
                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="OK"))

            elif request.command == 10:
                # for chat message(no operation)
                if self._findUserInChannel(request.id, request.focusChan):
                    _chat = ['g', request.focusChan, request.id, request.message]
                    self._chatLog.append(_chat)
                    #print(self._chatlog)
                    
                    _messages.append(
                        minichat_pb2.Resp_MessageToClient(
                            message="OK"))

            elif request.command == 20:
                # for all message(/all)
                _chat = ['a', ' ', request.id, request.message]
                self._chatLog.append(_chat)
                
                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="OK"))

            elif request.command == 101:
                # for channel list(/chanlist)
                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="Channel List:"))
                _chanlist = self._chanList.keys()
                
                for _chan in _chanlist:
                    _messages.append(
                        minichat_pb2.Resp_MessageToClient(
                            message="#" + _chan))

                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="OK"))

            elif request.command == 102:
                # for user list(/userlist)
                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="# %s User List:" % request.focusChan))

                for _user in self._chanList[request.focusChan]:
                    _messages.append(
                        minichat_pb2.Resp_MessageToClient(
                            message=_user))
                    _messages.append(_user)
                
                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="OK"))

            elif request.command == 201:
                # for channel join(/join (#channel))
                if request.message not in self._chanList.keys():
                    _list = []
                    _list.append(request.id)
                    self._chanList[request.message] = _list
                else:
                    if request.id not in self._chanList[request.message]:
                        self._chanList[request.message].append(request.id)
                
                print("\"{}\" joined channel \"{}\"".format(request.id, request.message))
                _messages.append(
                    minichat_pb2.Resp_MessageToClient(
                        message="OK"))
                
            elif request.command == 202:
                # for channel leave(/leave (#channel))
                if self._removeUserbyChanList(request.id, request.message):
                    _messages.append(
                        minichat_pb2.Resp_MessageToClient(
                            message="OK"))
                else:
                    _messages.append(
                        minichat_pb2.Resp_MessageToClient(
                            message="ERR"))

            # update time for active user
            self._lrudict.goBack(request.id)
            self._lrudict.updateValue(request.id, self._nowTime)

            # send messages, if contained messages in list
            async for _message in _messages:
                yield _message
        
        async def AliveSignal(self, request: minichat_pb2.Req_User,
            unused_context) -> minichat_pb2.Resp_AliveToClient:
            # signaling 5 seconds by client
            if request.id in self._userList:
                 return minichat_pb2.Resp_AliveToClient(alive=True)
            return minichat_pb2.Resp_AliveToClient(alive=False)
    
    # mcServer Class Area
    def __init__(self) -> None:
        super().__init__()
        self._server = grpc.aio.server()
        self._mcServerServicer = self.mcServerServicer()
        self._connOpt = []

        self._asioLoop = asyncio.get_event_loop()

    # Private Task Functions
    async def _runServer(self) -> None:
        minichat_pb2_grpc.add_mcServerServicerServicer_to_server(
            self._mcServerServicer, self._server)
        self._server.add_insecure_port(str(self._connOpt[1]))
        
        await self._server.start()
        await self._server.wait_for_termination()

    def _procCont(self) -> None:
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self._mcServerServicer._connQuit = True
                self._server.stop()
                break

    async def _initEventLoop(self) -> None:
        _serverTask = asyncio.create_task(self._runServer())
        # _procContTask = asyncio.create_task(self._procCont())
        _pThread = threading.Thread(target=self._procCont, daemon=True)
        _pThread.start()

        await _serverTask
        _pThread.join()
        # await _procContTask

    # Public Functions
    def start(self, connOpt: list) -> None:
        self._connOpt = connOpt

        self._asioLoop.run_until_complete(self._initEventLoop())
        self._asioLoop.close()