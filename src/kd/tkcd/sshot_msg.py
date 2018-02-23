#! /usr/bin/env python

from ctypes import *
from kd.util.logger import getLogger
from kd.tkcd import TKCD_CMD_TYPE

logger = getLogger(__name__)

def getAddSShotMsg(cltOpq, readonly, entries):
    slotCnt  = len(entries)
    pLen = 32 + slotCnt * 8
    msg = eval('SshotMsg_%d' % slotCnt)(0xF3F3, 0, 0, pLen, TKCD_CMD_TYPE.ADD_SNAPSHOT.getVal(), 0, 0, cltOpq,
                       0xcacacacadeafbeaf, 0, readonly, 0, len(entries), 0)
    for idx in range( len(entries) ):
        msg.entries[2 * idx    ] = entries[idx][0]
        msg.entries[2 * idx + 1] = entries[idx][1]
    return msg

def getAddSShotMsg(cltOpq, readonly, entries):
    slotCnt  = len(entries)
    pLen = 32 + slotCnt * 8
    msg = eval('SshotMsg_%d' % slotCnt)(0xF3F3, 0, 0, pLen, TKCD_CMD_TYPE.DEL_SNAPSHOT.getVal(), 0, 0, cltOpq,
                       0xcacacacadeafbeaf, 0, readonly, 0, len(entries), 0)
    for idx in range( len(entries) ):
        msg.entries[2 * idx    ] = entries[idx][0]
        msg.entries[2 * idx + 1] = entries[idx][1]
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
                ("panelSeqNo",  c_ulonglong),
                ("tileSeqNo",   c_ulonglong),
                ("readOnly",    c_ubyte),
                ("padding",     c_ubyte),
                ("entryCnt",    c_ushort),
                ("padding2",    c_uint)]

    def __str__(self):
        if self.rc == 0:
            print self.payloadLen
            return "send %s-%s cmd %d-panels: %s" % (
                    "read-only" if bool(self.readOnly) else "read-write",
                    TKCD_CMD_TYPE.getEnum(self.cmdType),
                    self.entryCnt,
                    ','.join( "%d->%d" % (self.entries[2 * idx], self.entries[2 * idx + 1] )for idx in range(self.entryCnt)) )
        return "recv %s-%s rsp %d-panels: %s with rc %u" % (
                "read-only" if bool(self.readOnly) else "read-write",
                TKCD_CMD_TYPE.getEnum(self.cmdType),
                self.entryCnt,
                ','.join( "%d->%d" % (self.entries[2 * idx], self.entries[2 * idx + 1] )for idx in range(self.entryCnt)),
                self.rc)

    __repr__ = __str__

class SshotMsg_1(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 2)]

class SshotMsg_2(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 4)]

class SshotMsg_3(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 6)]

class SshotMsg_4(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 8)]

class SshotMsg_5(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 10)]

class SshotMsg_6(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 12)]

class SshotMsg_7(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 14)]

class SshotMsg_8(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 16)]

class SshotMsg_9(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 18)]

class SshotMsg_10(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 20)]

class SshotMsg_11(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 22)]

class SshotMsg_12(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 24)]

class SshotMsg_13(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 26)]

class SshotMsg_15(SshotMsg):
    _fields_ = [ ("entries",    c_uint * 28)]

if __name__ == '__main__':
    ''' Test this module here '''
    msg = getAddSShotMsg(0xcacacaca, True, [(11 + idx, 21 + idx) for idx in range(8)] )
    print msg
    msg.rc = 1
    print msg


