"""
Copyright (C) 2019 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""
import asyncio

"""
Just a thin wrapper around a socket.
It allows us to keep some other info along with it.
"""


import logging

from typing import Optional
from asyncio import StreamReader, StreamWriter
from asyncio import open_connection as open_socket_connection


#TODO: support SSL !!

logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.wrapper = None
        """
        self.lock = threading.Lock()
        """
        self.reader: Optional[StreamReader] = None
        self.writer: Optional[StreamWriter] = None

    async def a_connect(self):
        # TODO: Add error handling + timeout
        self.reader, self.writer = await open_socket_connection(self.host, self.port)

    async def a_recv_msg(self):
        try:
            reader = await self.reader.read(4096)
            return reader
        except asyncio.CancelledError:
            self.writer.close()
            await self.writer.wait_closed()

    async def a_send_msg(self, msg):
        try:
            if not self.isConnected():
                logger.debug("[async] sendMsg attempted while not connected")
                return None
            self.writer.write(msg)
            await self.writer.drain()
            return len(msg)
        except asyncio.CancelledError:
            return -1

    async def a_disconnect(self):
        self.disconnect_nb()
        await self.writer.wait_closed()

    def disconnect_nb(self):
        self.writer.close()

    async def connect(self):
        await self.a_connect()

    async def disconnect(self):
        # TODO: Handle exceptions
        await self.a_disconnect()

    def isConnected(self):
        return self.writer is not None

    def sendMsg(self, msg):
        if not self.isConnected():
            logger.debug("sendMsg attempted while not connected, releasing lock")
            return None
        self.writer.write(msg)
        return None

    async def recvMsg(self):
        try:
            if not self.isConnected():
                logger.debug("recvMsg attempted while not connected, releasing lock")
                return b""
            return await self.a_recv_msg()
        except asyncio.CancelledError:
            pass
