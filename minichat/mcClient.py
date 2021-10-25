#-*- coding: utf-8 -*-

import sys
import asyncio
from typing import AsyncIterable, Iterable

import threading
import time

import grpc

import minichat_pb2
import minichat_pb2_grpc

from etc import hashing

class mcClient(object):
    def __init__(self) -> None:
        super().__init__()

        self._connOpt = []
        self._client = None
        self._connection = None # this is stub
        self._connected = False

        self._user = hashing.genHash() # make 8-string hash for id
        self._focusChan = " "
        self._connQuit = False

        self._asioLoop = asyncio.get_event_loop()

    # Private Functions
    # def _makeCommandStream(self, command: int,
    #         message: str): -> AsyncIterable[minichat_pb2.Resp_MessageToClient]:
    #     yield self._connection.CommandStream(
    #         minichat_pb2.Req_MessageToServer(
    #             id=self._user, focusChan=self._focusChan, command=command, message=message))

    def _makeAliveSignal(self) -> minichat_pb2.Resp_AliveToClient:
        yield self._connection.AliveSignal(
                    minichat_pb2.Req_User(id=self._user, focusChan=self._focusChan))

    def _sendMessage(self, msg: str) -> None:
        _code = 0
        _msg = msg

        if _msg.find('/') == 0:
            if _msg.find('all') == 1:
                _code = 20
                _msg = _msg.replace('/all', '')
            elif _msg.find('chanlist') == 1:
                _code = 101
                _msg = _msg.replace('/chanlist', '')
            elif _msg.find('userlist') == 1:
                _code = 102
                _msg = _msg.replace('/userlist', '')
            elif _msg.find('join') == 1:
                _code = 201
                _msg = _msg.replace('/join', '')
            elif _msg.find('leave') == 1:
                _code = 202
                _msg = _msg.replace('/leave', '')
            else:
                # invaild
                print("Invaild Commands")
                return
            _msg = _msg.strip()
        else:
            _code = 10

        # _respMsg = self._makeCommandStream(_code, _msg)
        _respMsg = self._connection.CommandStream(
            minichat_pb2.Req_MessageToServer(
                id=self._user, focusChan=self._focusChan, command=_code, message=_msg))

        _storeMsg = ""
        for _msg in _respMsg:        
            print("{}".format(_msg.message))
            _storeMsg = _msg.message
        # check last message
        if _storeMsg.find('OK') == 0:
            if _code == 201:
                self._focusChan = _msg
                
            elif _code == 202:
                self._focusChan = ''

    # Private Task & Thread Functions
    def _listenThread(self) -> None:
        for _msg in self._connection.MessageStream(
            minichat_pb2.Req_User(id=self._user, focusChan=self._focusChan)):
            print("{}".format(str(_msg.message))) # for cli chat
    
    async def _aliveSignalTask(self) -> None:
        while not self._connQuit:
            if self._connected:
                _respMsg = self._makeAliveSignal()
                
                if not _respMsg.alive:
                    print("Connection Closed")
                    self._connected = False
                    self._connQuit = True
                    self._client.close()
            # this task sleep in 5 seconds
            await asyncio.sleep(5)

    async def _getKeyboardMessageTask(self) -> None:
        # looping infinitely
        while not self._connQuit:
            _msg = await asyncio.get_event_loop().run_in_executor(
                None, input, "{} > ".format(self._user))
            
            if len(_msg) > 0:
                self._sendMessage(_msg)

    async def _initSEquence(self) -> None:
        # _respMsg = self._makeCommandStream(1, "")
        _respMsg = self._connection.CommandStream(
            minichat_pb2.Req_MessageToServer(
                id=self._user, focusChan=self._focusChan, command=1, message=""))

        async for _msg in _respMsg:
            if _msg.message == "OK":
                print("Connected")
                self._connected = True
            else:
                print("Connect Fail. Exit")
                self._connQuit = True
                self._client.close()

    async def _runClient(self) -> None:
        async with grpc.aio.insecure_channel(str(self._connOpt[1])) as self._client:
            self._connection = minichat_pb2_grpc.mcServerServicerStub(self._client)

            # call CommandStream RPC in Server for initial info
            await self._initSEquence()

            _lThread = threading.Thread(target=self._listenThread, daemon=True)
            
            await asyncio.gather(self._aliveSignalTask(), self._getKeyboardMessageTask())
            
            _lThread.join()

    def _procCont(self) -> None:
        while not self._connQuit:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self._connQuit = True
                self._connected = False
                self._client.close()
                break

    async def _initEventLoop(self) -> None:
        _ClientTask = asyncio.create_task(self._runClient())
        # _procContTask = asyncio.create_task(self._procCont())
        _pThread = threading.Thread(target=self._procCont, daemon=True)
        _pThread.start()

        await _ClientTask
        _pThread.join()
        # await _procContTask

    def start(self, connOpt: list) -> None:
        self._connOpt = connOpt
        
        self._asioLoop.run_until_complete(self._initEventLoop())
        self._asioLoop.close()