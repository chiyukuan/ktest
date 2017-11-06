#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Define the tkcd msg hdr

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import socket
from ctypes import *

class HdrMsg(Structure):
    _fields_ = [("msgSig",     c_ushort),
                ("rc",         c_ubyte),
                ("isRsp",      c_ubyte),
                ("payloadLen", c_uint),]

    @staticmethod
    def size():
        return sizeof(HdrMsg)

    def htonCopy(self):
        dst = HdrMsg()
        pointer(dst)[0] = self
        dst.payloadLen = socket.htonl( self.payloadLen )
        return dst

    def ntohCopy(self):
        dst = HdrMsg()
        pointer(dst)[0] = self
        dst.payloadLen = socket.ntohl( self.payloadLen )
        return dst

    def __str__(self):
        return "CmdSig %u rc %u payloadLen %u" % (
                self.msgSig, self.rc, self.payloadLen)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    hdrMsg = HdrMsg(1, 2, 1, 128)
    print hdrMsg
    print hdrMsg.htonCopy()
    print hdrMsg.ntohCopy()
    print sizeof(hdrMsg)
    hdrMsg = HdrMsg()
    print hdrMsg
    print sizeof(hdrMsg)


