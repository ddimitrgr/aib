from typing import Optional

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from aib.reader import EReader
from aib.connection import Connection


"""
Copyright (C) 2019 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""


"""
The main class to use from API user's point of view.
It takes care of almost everything:
- implementing the requests
- creating the answer decoder
- creating the connection to TWS/IBGW
The user just needs to override EWrapper methods to receive the answers.
"""

import logging
import socket
import asyncio

from ibapi import (decoder, comm)
from ibapi.message import OUT
from ibapi.common import * # @UnusedWildImport
from ibapi.comm import (make_field, make_field_handle_empty)
from ibapi.utils import (current_fn_name, BadMessage)
from ibapi.errors import * #@UnusedWildImport
from ibapi.server_versions import * # @UnusedWildImport
from ibapi.utils import ClientException
from asyncio import Queue, QueueEmpty

#TODO: use pylint

logging.getLogger('asyncio').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


class AsyncRxClient(EClient):

    def __init__(self, wrapper: EWrapper):
        EClient.__init__(self, wrapper=wrapper)
        # self.msg_queue = queue.Queue()
        self.msg_queue = Queue()
        self.wrapper = wrapper
        self.decoder: Optional[decoder.Decoder] = None
        self.reader: Optional[EReader] = None
        self.reset()

    async def a_send_msg(self, msg):
        full_msg = comm.make_msg(msg)
        logger.info("%s %s %s", "SENDING", current_fn_name(1), full_msg)
        await self.conn.a_send_msg(full_msg)

    async def startApi(self):
        """  Initiates the message exchange between the client application and
        the TWS/IB Gateway. """

        self.logRequest(current_fn_name(), vars())

        if not self.isConnected():
            self.wrapper.error(NO_VALID_ID, NOT_CONNECTED.code(),
                               NOT_CONNECTED.msg())
            return

        try:

            VERSION = 2

            msg = make_field(OUT.START_API) \
                  + make_field(VERSION)    \
                  + make_field(self.clientId)

            if self.serverVersion() >= MIN_SERVER_VER_OPTIONAL_CAPABILITIES:
                msg += make_field(self.optCapab)

        except ClientException as ex:
            self.wrapper.error(NO_VALID_ID, ex.code, ex.msg + ex.text)
            return

        await self.a_send_msg(msg)

    async def connect(self, host, port, clientId):
        """This function must be called before any other. There is no
        feedback for a successful connection, but a subsequent attempt to
        connect will return the message \"Already connected.\"

        host:str - The host name or IP address of the machine where TWS is
            running. Leave blank to connect to the local host.
        port:int - Must match the port specified in TWS on the
            Configure>API>Socket Port field.
        clientId:int - A number used to identify this client connection. All
            orders placed/modified from this client will be associated with
            this client identifier.

            Note: Each client MUST connect with a unique clientId."""


        try:
            self.host = host
            self.port = port
            self.clientId = clientId
            logger.debug("Connecting to %s:%d w/ id:%d", self.host, self.port, self.clientId)

            self.conn = Connection(self.host, self.port)

            await self.conn.connect()
            self.setConnState(EClient.CONNECTING)

            #TODO: support async mode

            v100prefix = "API\0"
            v100version = "v%d..%d" % (MIN_CLIENT_VER, MAX_CLIENT_VER)

            if self.connectionOptions:
                v100version = v100version + " " + self.connectionOptions

            #v100version = "v%d..%d" % (MIN_CLIENT_VER, 101)
            msg = comm.make_msg(v100version)
            logger.debug("msg %s", msg)
            msg2 = str.encode(v100prefix, 'ascii') + msg
            logger.debug("REQUEST %s", msg2)
            await self.conn.a_send_msg(msg2)

            self.decoder = decoder.Decoder(self.wrapper, self.serverVersion())
            fields = []

            #sometimes I get news before the server version, thus the loop
            while len(fields) != 2:
                self.decoder.interpret(fields)
                buf = await self.conn.recvMsg()
                if not self.conn.isConnected():
                    # recvMsg() triggers disconnect() where there's a socket.error or 0 length buffer
                    # if we don't then drop out of the while loop it infinitely loops
                    logger.warning('Disconnected; resetting connection')
                    self.reset()
                    return
                logger.debug("ANSWER %s", buf)
                if len(buf) > 0:
                    (size, msg, rest) = comm.read_msg(buf)
                    logger.debug("size:%d msg:%s rest:%s|", size, msg, rest)
                    fields = comm.read_fields(msg)
                    logger.debug("fields %s", fields)
                else:
                    fields = []

            (server_version, conn_time) = fields
            server_version = int(server_version)
            logger.debug("ANSWER Version:%d time:%s", server_version, conn_time)
            self.connTime = conn_time
            self.serverVersion_ = server_version
            self.decoder.serverVersion = self.serverVersion()

            self.setConnState(EClient.CONNECTED)

            # self.reader = reader.EReader(self.conn, self.msg_queue)
            self.reader = EReader(self.conn, self.msg_queue)
            # self.reader.start()   # start thread
            asyncio.ensure_future(self.reader.run())
            logger.info("sent startApi")
            await self.startApi()
            self.wrapper.connectAck()
        except socket.error:
            if self.wrapper:
                self.wrapper.error(NO_VALID_ID, CONNECT_FAIL.code(), CONNECT_FAIL.msg())
            logger.info("could not connect")
            await self.disconnect()

    async def disconnect(self):
        """Call this function to terminate the connections with TWS.
        Calling this function does not cancel orders that have already been
        sent."""

        self.setConnState(EClient.DISCONNECTED)
        if self.conn is not None:
            logger.info("disconnecting")
            await self.conn.disconnect()
            self.wrapper.connectionClosed()
            self.reset()

    async def run(self):
        """This is the function that has the message loop."""
        # TODO: How to handle CancelledError ?
        while True:
            try:
                while True:  # self.isConnected() or not self.msg_queue.empty():
                    try:
                        try:
                            text = await self.msg_queue.get()  # block=True, timeout=0.2)
                            if len(text) > MAX_MSG_LEN:
                                self.wrapper.error(NO_VALID_ID, BAD_LENGTH.code(),
                                                   "%s:%d:%s" % (BAD_LENGTH.msg(), len(text), text))
                                break
                        except QueueEmpty:
                            # except queue.Empty:
                            logger.debug("queue.get: empty")
                            self.msgLoopTmo()
                        else:
                            fields = comm.read_fields(text)
                            logger.debug("fields %s", fields)
                            self.decoder.interpret(fields)
                            self.msgLoopRec()
                    except (KeyboardInterrupt, SystemExit):
                        logger.info("detected KeyboardInterrupt, SystemExit")
                        self.keyboardInterrupt()
                        self.keyboardInterruptHard()
                    except BadMessage:
                        logger.info("BadMessage")

                    logger.debug("conn:%d queue.sz:%d",
                                 self.isConnected(),
                                 self.msg_queue.qsize())
            except asyncio.CancelledError as e:
                break
            # finally:
            #    await self.disconnect()
