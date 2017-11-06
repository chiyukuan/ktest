#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Define IO related message.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import socket
from ctypes import *
from kd.util.logger import getLogger
from kd.tkcd import TKCD_CMD_TYPE

logger = getLogger(__name__)

def getRdMsg(cltOpq, tKey, lba, blocks, cltSeqNo=0xfead, panelId=0):
    ioMsg = IoMsg(0xF1F1, 0, 0, IoMsg.msgSize() - 8,
                  TKCD_CMD_TYPE.READ.getVal(),
                  0, 0, cltSeqNo, panelId, blocks, lba, tKey, cltOpq)
    return ioMsg

def getWrMsg(cltOpq, tKey, lba, blocks, cltSeqNo=0xfeee, panelId=0):
    ioMsg = IoMsg(0xF1F1, 0, 0, IoMsg.msgSize() - 8 + (blocks * 4096),
                  TKCD_CMD_TYPE.WRITE.getVal(),
                  0, 0, cltSeqNo, panelId, blocks, lba, tKey, cltOpq)
    return ioMsg

class IoMsg(Structure):
    _fields_ = [("msgSig",      c_ushort),
                ("rc",          c_ubyte),
                ("isRsp",       c_ubyte),
                ("payloadLen",  c_uint),
                ("cmdType",     c_ubyte),
                ("padding",     c_ubyte),
                ("status",      c_ushort),
                ("cltSeqNo",    c_uint),
                ("panelId",     c_uint),
                ("blocks",      c_uint),
                ("lba",         c_ulonglong),
                ("tKey",        c_ulonglong),
                ("cltOpq",      c_ulonglong),]

    @staticmethod
    def msgSize():
        return sizeof(IoMsg)

    def htonCopy(self):
        dst = IoMsg()
        pointer(dst)[0] = self
        dst.payloadLen = socket.htonl( self.payloadLen )
        dst.status     = socket.htons( self.status )
        dst.blocks     = socket.htonl( self.blocks )
        dst.lba        = socket.htonl( self.lba & 0xffffffff)
        dst.lba      <<= 32
        dst.lba       += socket.htonl( self.lba >> 32)
        return dst

    def ntohCopy(self):
        dst = IoMsg()
        pointer(dst)[0] = self
        dst.payloadLen = socket.ntohl( self.payloadLen )
        dst.status     = socket.ntohs( self.status )
        dst.blocks     = socket.ntohl( self.blocks )
        dst.lba        = socket.ntohl( self.lba & 0xffffffff)
        dst.lba      <<= 32
        dst.lba       += socket.ntohl( self.lba >> 32)
        return dst
        
    def __str__(self):
        if self.rc == 0:
            if self.cmdType == 1:
                return "payload %d clt 0x%lx send rd %u blocks cmd at lba 0x%lx with key 0x%lx" % (
                        self.payloadLen, self.cltSeqNo, self.blocks, self.lba, self.tKey)
            else:
                return "payload %d clt 0x%lx send wr %u blocks cmd at lba 0x%lx with key 0x%lx" % (
                        self.payloadLen, self.cltSeqNo, self.blocks, self.lba, self.tKey)

        if self.cmdType == 1:
            return "payload %d clt 0x%lx send rd %u blocks cmd at lba 0x%lx rc %u(%u)" % (
                    self.payloadLen, self.cltSeqNo, self.blocks, self.lba, self.rc, self.status)
        else:
            return "payload %d clt 0x%lx send wr %u blocks cmd at lba 0x%lx rc %u(%u)" % (
                    self.payloadLen, self.cltSeqNo, self.blocks, self.lba, self.rc, self.status)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    ioMsg = getRdMsg(0xcacacaca, 0x10101, 0x200, 4096)
    print ioMsg
    ioMsg.rc = 1
    print ioMsg
    ioMsg = getWrMsg(0xcacacaca, 0x10101, 0x200, 4096)
    print ioMsg
    ioMsg2 = ioMsg.htonCopy()
    print "Msg 2: %s" % ioMsg2
    ioMsg3 = ioMsg2.ntohCopy()
    print "Msg 3: %s" % ioMsg3
    ioMsg.rc = 1
    print "Msg 1: %s" % ioMsg
    print IoMsg.msgSize()

    print getWrMsg(0xcacacacb, 0, 0, 1)
