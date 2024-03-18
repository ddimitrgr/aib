"""
Copyright (C) 2019 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
 and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""


"""
The EReader runs in a separate threads and is responsible for receiving the
incoming messages.
It will read the packets from the wire, use the low level IB messaging to
remove the size prefix and put the rest in a Queue.
"""


import logging

from ibapi import comm
from asyncio import CancelledError, Queue, all_tasks, current_task

logger = logging.getLogger(__name__)


class EReader:
    def __init__(self, conn, msg_queue: Queue):
        super().__init__()
        self.conn = conn
        self.msg_queue = msg_queue

    async def run(self):
        # TODO: Check error handling for CancelledError & RuntimeError
        try:
            logger.debug("EReader thread started")
            buf = b""
            while self.conn.isConnected():

                data = await self.conn.recvMsg()
                if data is None:
                    # Connection closed:
                    return
                logger.debug("reader loop, recvd size %d", len(data))
                buf += data

                while len(buf) > 0:
                    (size, msg, buf) = comm.read_msg(buf)
                    #logger.debug("resp %s", buf.decode('ascii'))
                    logger.debug("size:%d msg.size:%d msg:|%s| buf:%s|", size,
                        len(msg), buf, "|")

                    if msg:
                        # self.msg_queue.put(msg)
                        self.msg_queue.put_nowait(msg)
                    else:
                        logger.debug("more incoming packet(s) are needed ")
                        break

            logger.debug("EReader thread finished")
        except CancelledError as e:
            logger.exception('EReader.run() exiting ...')
        except RuntimeError as e2:
            logger.exception('unhandled exception in EReader thread')