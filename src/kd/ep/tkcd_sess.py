#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import socket
import time
import os
import random
from kd.util.logger import getLogger
from kd.util.url import Url
from kd.util.rc_msg import RC
from kd.tkcd.hdr_msg import HdrMsg
from kd.tkcd.dev_msg import DevMsg
from kd.tkcd.tile_msg import TileMsg
from kd.tkcd.io_msg import IoMsg

logger = getLogger(__name__)

class TkcdSess(object):
    ''' Short summary, should fit on one line

    Attributes:
        attr1 (str): description ...
        attr2 ....
    '''

    def __init__(self, url, dFN, dFMSz=16):
        self.url  = url
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hdrMsg = HdrMsg()
        self.dFN    = dFN
        self.dFMSz  = dFMSz
        self.dFSzMask = (self.dFMSz << 20) - 1
        if dFN is None:
            self.inBuf = bytearray( 1025 * 1024 )
            self.dFile = None
        else:
            if not os.path.isfile(self.dFN):
                self.dFile = open(self.dFN, "wb")

                # write extra mByte 
                for idx in range( dFMSz + 1 ):
                    byteArray = bytearray(self._randbytes(1024*1024))
                    self.dFile.write( byteArray )
                self.dFile.flush()
                self.dFile.close()

            self.dFile = open(self.dFN, "r+b")

            self.inBuf = bytearray( 1025 * 1024 )

    def connect(self):
        self.conn.connect( (self.url.hostname, self.url.port) )

    def close(self):
        self.conn.close()

    def send(self, cmdMsg, timeout=-1):
        self.cmdMsg = cmdMsg
        if self.cmdMsg.msgSig != 0xF1F1:
            self.conn.sendall(cmdMsg)
        else:
            htonMsg = self.cmdMsg.htonCopy()
            self.conn.sendall(htonMsg)
            # send data
            dataSize = cmdMsg.payloadLen - (IoMsg.msgSize() - HdrMsg.size())
            if dataSize > 0:
                dBuf    = bytearray( self._randbytes(dataSize) )
                dBufSig = bytearray( self._randbytes(6) )
                dBufSig[0] = (cmdMsg.lba    >> 24) & 0xff
                dBufSig[1] = (cmdMsg.lba    >> 16) & 0xff
                dBufSig[2] = (cmdMsg.lba    >>  8) & 0xff
                dBufSig[3] = (cmdMsg.lba    >>  0) & 0xff
                dBufSig[4] = (cmdMsg.blocks >>  8) & 0xff
                dBufSig[5] = (cmdMsg.blocks >>  0) & 0xff
                #print "DataSig %02x%02x %02x%02x %02x%02x" % (
                #        dBufSig[0], dBufSig[1], dBufSig[2],
                #        dBufSig[3], dBufSig[4], dBufSig[5])
                idx = 0
                while idx < dataSize:
                    dBuf[idx+0] = dBufSig[0]
                    dBuf[idx+1] = dBufSig[1]
                    dBuf[idx+2] = dBufSig[2]
                    dBuf[idx+3] = dBufSig[3]
                    dBuf[idx+4] = dBufSig[4]
                    dBuf[idx+5] = dBufSig[5]

                    idx += 4096
                self.conn.sendall(dBuf)
                if self.dFile is not None:
                    addr = (cmdMsg.lba * 4096) & self.dFSzMask
                    self.dFile.seek( addr )
                    self.dFile.write( dBuf )
                    self.dFile.flush()

    sendline = send

    def expect(self, seps=-1, timeout=-1):
        # @todo need to handle timeout case
        rc = RC.OK

        view = memoryview(self.inBuf)

        toread = HdrMsg.size() ;
        while toread > 0:
            nbytes = self.conn.recv_into(view, toread)
            view = view[nbytes:]
            toread -= nbytes

        hdrMsg = HdrMsg.from_buffer_copy(self.inBuf)
        if hdrMsg.msgSig == 0xF1F1:
            hdrMsg = hdrMsg.ntohCopy()

        toread = hdrMsg.payloadLen
        while toread:
            nbytes = self.conn.recv_into(view, toread)
            view = view[nbytes:]
            toread -= nbytes

        if self.cmdMsg.msgSig == 0xF1F1:
            rspMsg = IoMsg.from_buffer_copy(self.inBuf)
            rspMsg = rspMsg.ntohCopy()
            if rspMsg.rc != 1:
                rc = RC.ERROR

            elif rspMsg.cmdType == 1 and self.dFile is not None:
                addr    = (rspMsg.lba * 4096) & self.dFSzMask
                byteCnt = rspMsg.blocks * 4096
                self.dFile.seek( addr )
                expected = bytearray(self.dFile.read( byteCnt ))
                returned = self.inBuf[ IoMsg.msgSize():IoMsg.msgSize() + byteCnt]

                for idx in range( byteCnt ):
                    if expected[idx] != returned[idx]:
                        logger.error("data corruption: offset %x expected 0x%02x return 0x%02x",
                                idx, expected[idx], returned[idx])
                        bIdx = idx & 0xfffff000
                        lba    = (returned[bIdx  ] << 24) + (returned[bIdx+1] << 16) + (returned[bIdx+2] <<  8) + (returned[bIdx+3]) ;
                        blocks = (returned[bIdx+4] <<  8) + (returned[bIdx+5])
                        logger.error("returned: last tx lba 0x%x blocks %d", lba, blocks)
                        lba    = (expected[bIdx  ] << 24) + (expected[bIdx+1] << 16) + (expected[bIdx+2] <<  8) + (expected[bIdx+3]) ;
                        blocks = (expected[bIdx+4] <<  8) + (expected[bIdx+5])
                        logger.error("expected: last tx lba 0x%x blocks %d", lba, blocks)
                        rc = RC.ERROR
                        break

        elif self.cmdMsg.msgSig == 0xF2F2:
            rspMsg = DevMsg.from_buffer_copy(self.inBuf)
            if rspMsg.rc != 1:
                rc = RC.ERROR
        elif self.cmdMsg.msgSig == 0xF3F3:
            rspMsg = TileMsg.from_buffer_copy(self.inBuf)
            if rspMsg.rc != 1:
                rc = RC.ERROR
        else:
            return RC.NOT_YET, "unknown message type"

        logger.debug("rsp Msg %s", rspMsg)
        return rc, rspMsg

    def _randbytes(self, size):
        for _ in xrange( size ):
            yield random.getrandbits(8)

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    '''
    sess = TkcdSess(Url.fromStr("tcp://127.0.0.1:5017"))
    sess.connect()
    sess.close()
    '''

    myFile = open("/tmp/testit.txt", "wb")
    for c in range(50, 70):
        myFile.write(chr(c))

    myFile.close()


