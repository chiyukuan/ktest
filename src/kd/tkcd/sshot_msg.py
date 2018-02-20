#! /usr/bin/env python

from ctypes import *
from kd.util.logger import getLogger
from kd.tkcd import TKCD_CMD_TYPE

logger = getLogger(__name__)

def getAddSShotMsg(cltOpq, readonly, panelIds):
    panelCnt = len(panelIds)
    pLen  = 40
    if panelCnt > 7:
        pLen += (panelCnt - 7) * 4
    msg = SshotMsg(0xF3F3, 0, 0, pLen, TKCD_CMD_TYPE.ADD_SNAPSHOT.getVal(), 0, 0, cltOpq,
                   readonly, 0, len(panelIds))
    for idx in range( len(panelIds) ):
        msg.panelIds[idx] = panelIds[idx]
    return msg

def getDelSShotMsg(cltOpq, readonly, panelIds):
    msg = SshotMsg(0xF3F3, 0, 0, 40, TKCD_CMD_TYPE.DEL_SNAPSHOT.getVal(), 0, 0, cltOpq,
                   readonly, 0, len(panelIds))
    for idx in range( len(panelIds) ):
        msg.panelIds[idx] = panelIds[idx]
    return msg

class SshotMsg(Structure):
    _fields_ = [("msgSig",      c_ushort),
                ("rc",          c_ubyte),
                ("isRsp",       c_ubyte),
                ("payloadLen",  c_uint),
                ("cmdType",     c_ubyte),
                ("msgOpq",      c_ubyte),
                ("status",      c_ushort),
                ("cltOpq",      c_uint),
                ("readOnly",    c_ubyte),
                ("padding",     c_ubyte),
                ("panelCnt",    c_ushort),
                ("panelIds",    c_uint * 8)]

    def __str__(self):
        if self.rc == 0:
            print self.payloadLen
            return "send %s-%s cmd %d-panels: %s" % (
                    "read-only" if bool(self.readOnly) else "read-write",
                    TKCD_CMD_TYPE.getEnum(self.cmdType),
                    self.panelCnt,
                    ','.join(str( self.panelIds[idx] ) for idx in range(self.panelCnt)) )
        return "recv %s-%s rsp %d-panels: %s with rc %u" % (
                "read-only" if bool(self.readOnly) else "read-write",
                TKCD_CMD_TYPE.getEnum(self.cmdType),
                self.panelCnt,
                ','.join(str( self.panelIds[idx] ) for idx in range(self.panelCnt)),
                self.rc)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    msg = getAddSShotMsg(0xcacacaca, True, (11,12,13,14,15,15,16,18))
    print msg
    msg.rc = 1
    print msg


