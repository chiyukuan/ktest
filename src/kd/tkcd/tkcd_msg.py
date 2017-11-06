#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from ctypes import *
from kd.util.logger import getLogger

logger = getLogger(__name__)

def getTkcdAddMsg(dockNodeId, ip, port, dockPlateId=1, virtualRackId=1):
    if type(ip) is str:
        segs = map(int, ip.split('.'))
        ip = (segs[0] << 24) + (segs[1] << 16) + (segs[2] << 8) + segs[3]
    msg = TkcdMsg(0xF3F3, 0, 0, 40, 31, 0, 0, 0, dockNodeId, dockPlateId, virtualRackId,
                  ip, port)
    return msg

class TkcdMsg(Structure):
    _fields_ = [("msgSig",         c_ushort),
                ("rc",             c_ubyte),
                ("isRsp",          c_ubyte),
                ("payloadLen",     c_uint),
                ("cmdType",        c_ubyte),
                ("padding",        c_ubyte),
                ("status",         c_ushort),
                ("cltOpq",         c_uint),
                ("dockNodeId",     c_uint),
                ("dockPlateId",    c_uint),
                ("virtualRackId",  c_uint),
                ("ip",             c_uint),
                ("port",           c_uint),
                ("padding2_1",     c_uint),
                ("padding2_2",     c_uint),
                ("padding2_3",     c_uint)]

    def getCmdName(self):
        if self.cmdType == 31:
            return 'TKCD_ADD'
        if self.cmdType == 32:
            return 'TKCD_DEL'
        if self.cmdType == 33:
            return 'TKCD_UPD'
        if self.cmdType == 34:
            return 'TKCD_REG'
        return 'unknow'

    def __str__(self):
        ipAddr = "%d.%d.%d.%d" % ( (self.ip >> 24) & 0xff,
                                   (self.ip >> 16) & 0xff,
                                   (self.ip >>  8) & 0xff,
                                   (self.ip >>  0) & 0xff)
        if self.rc == 0:
            return "%s tkcd.%d @ %s:%u" % (
                    self.getCmdName(), self.dockNodeId, ipAddr, self.port)
        return "%s tkcd.%d @ %s:%u with rc %u" % (
                self.getCmdName(), self.dockNodeId, ipAddr, self.port, self.rc)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    msg = getTkcdAddMsg(1, "1.2.3.4", 5678)
    print msg


