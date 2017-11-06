#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Define device related message.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from ctypes import *
from kd.util.logger import getLogger
from kd.tkcd import TKCD_CMD_TYPE

logger = getLogger(__name__)

def getAddDevMsg(mPath, dType=1, dBSize=4096, dBlocks=5242880):
    devMsg = DevMsg(0xF2F2, 0, 0, DevMsg.size() - 8,
                    TKCD_CMD_TYPE.DEV_ADD.getVal(),
                    0, 0, 0, dBSize, dBlocks, dType, mPath)
    return devMsg

def getDelDevMsg(mPath, dType=1, dBSize=0, dBlocks=0):
    devMsg = DevMsg(0xF2F2, 0, 0, DevMsg.size() - 8,
                    TKCD_CMD_TYPE.DEV_DEL.getVal(),
                    0, 0, 0, dBSize, dBlocks, dType, mPath)
    return devMsg

def getErrDevMsg(mPath, dType=1, dBSize=0, dBlocks=0):
    devMsg = DevMsg(0xF2F2, 0, 0, DevMsg.size() - 8,
                    TKCD_CMD_TYPE.DEV_ERR.getVal(),
                    0, 0, 0, dBSize, dBlocks, dType, mPath)
    return devMsg

def getErrDevIoMsg(mPath, ePol=None):
    if ePol is None:
        ePol = [0xffff, 0xffff, 0xffff, 0xffff]

    rRetry, wRetry, rErrMax, wErrMax = \
            [0xffff if x is None else x for x in ePol]

    dBSize  = 0
    dBlocks = (wRetry  << 16) + rRetry
    dType   = (wErrMax << 16) + rErrMax
    devMsg = DevMsg(0xF2F2, 0, 0, DevMsg.size() - 8,
                    TKCD_CMD_TYPE.DEV_ERR_IO.getVal(),
                    0, 0, 0, dBSize, dBlocks, dType, mPath)
    return devMsg

class DevMsg(Structure):
    _fields_ = [("msgSig",      c_ushort),
                ("rc",          c_ubyte),
                ("isRsp",       c_ubyte),
                ("payloadLen",  c_uint),
                ("cmdType",     c_ubyte),
                ("padding",     c_ubyte),
                ("status",      c_ushort),
                ("cltOpq",      c_uint),
                ("dBSize",      c_uint),
                ("dBlocks",     c_uint),
                ("dtype",       c_uint),
                ("mPath",       c_char * 100),]

    @staticmethod
    def size():
        return sizeof(DevMsg)

    def getCmdName(self):
        if self.cmdType == 11:
            return "AddDev"
        if self.cmdType == 13:
            return "DelDev"
        if self.cmdType == 14:
            return "ErrDev"
        if self.cmdType == 14:
            return "ErrDevIo"

        return "Unknow"

    def __str__(self):
        return "%s device at %s" % (self.getCmdName(), self.mPath)

    __repr__ = __str__

if __name__ == '__main__':
    devMsg = getAddDevMsg( '/kodiak/dock/0011fea2209830/docknode/1//mnt/0', 0)
    print devMsg
    print sizeof(DevMsg)
    print DevMsg.size()
    ''' Test this module here '''


