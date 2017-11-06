#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Define tile related message

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from ctypes import *
from kd.util.logger import getLogger
from kd.tkcd import TKCD_CMD_TYPE, TKCD_PROT_TYPE, hasDockProt

logger = getLogger(__name__)

def getBindTileMsg(cltOpq, panelId, tileSetId, pTypeKey):
    pType = TKCD_PROT_TYPE.getEnum( pTypeKey )
        
    cmdType = TKCD_CMD_TYPE.DOCK_BIND if hasDockProt(pType) else TKCD_CMD_TYPE.NODE_BIND
    tileMsg = TileMsg(0xF3F3, 0, 0, 88, cmdType.getVal(), 0, 0, cltOpq, 0, 0, panelId, tileSetId,
                      4096, 0, pType.getVal(), 1, 0,0,0,0,0xcacacacadeafbeaf, 0, 0)
    return tileMsg

def getUnbdTileMsg(cltOpq, panelId, tileSetId, pTypeKey):
    pType = TKCD_PROT_TYPE.getEnum( pTypeKey )
    cmdType = TKCD_CMD_TYPE.DOCK_UNBIND if hasDockProt(pType) else TKCD_CMD_TYPE.NODE_UNBIND

    tileMsg = TileMsg(0xF3F3, 0, 0, 88, cmdType.getVal(), 0, 0, cltOpq, 0, 0, panelId, tileSetId,
                      4096, 0, pType.getVal(), 1, 0,0,0,0,0, 0, 0)
    return tileMsg

def getDelPanelMsg(cltOpq, panelId, pTypeKey):
    pType = TKCD_PROT_TYPE.getEnum( pTypeKey )
    tileMsg = TileMsg(0xF3F3, 0, 0, 88, TKCD_CMD_TYPE.DEL_PANEL.getVal(), 0, 0, cltOpq, 0, 0, panelId, 0,
                     4096, 0, pType.getVal(), 1, 0,0,0,0,0, 0, 0)
    return tileMsg

class TileMsg(Structure):
    _fields_ = [("msgSig",         c_ushort),
                ("rc",             c_ubyte),
                ("isRsp",          c_ubyte),
                ("payloadLen",     c_uint),
                ("cmdType",        c_ubyte),
                ("padding",        c_ubyte),
                ("status",         c_ushort),
                ("cltOpq",         c_uint),
                ("panelSeqNo",     c_ulonglong),
                ("tileSeqNo",      c_ulonglong),
                ("panelId",        c_uint),
                ("tileSetId",      c_uint),
                ("blockSize",      c_uint),
                ("tileGrpIdx",     c_uint),

                ("protectionType", c_ubyte),
                ("tileType",       c_ubyte),
                ("tKeyCnt",        c_ushort),
                ("dNodeId",        c_uint),
                ("dNodeId2",       c_uint),
                ("dNodeId3",       c_uint),
                ("tKey",           c_ulonglong),
                ("tKey2",          c_ulonglong),
                ("tKey3",          c_ulonglong),
                ("tileCntFree",    c_uint),
                ("tileCntAllo",    c_uint)]

    def __str__(self):
        if self.rc == 0:
            # command msg
            return "send %s %s-tile cmd at %u@%u clt 0x%lx" %(
                    TKCD_CMD_TYPE.getEnum(self.cmdType),
                    TKCD_PROT_TYPE.getEnum(self.protectionType),
                    self.tileSetId, self.panelId, self.cltOpq)
        
        # response msg
        if self.tKeyCnt == 3:
            keys = "3-key 0x%lx@%d 0x%lx@%d 0x%lx@%d" % (
                    self.tKey,  self.dNodeId,
                    self.tKey2, self.dNodeId2,
                    self.tKey3, self.dNodeId3 )
        elif self.tKeyCnt == 2:
            keys = "2-key 0x%lx@%d 0x%lx@%d" % (
                    self.tKey,  self.dNodeId,
                    self.tKey2, self.dNodeId2 )
        elif self.tKeyCnt == 1:
            keys = "1-key 0x%lx" % ( self.tKey )
        else:
            keys = "rc %u" % self.rc

        return "recv %s %s-tile rsp at %u@%u clt 0x%lx with %s" %(
                TKCD_CMD_TYPE.getEnum(self.cmdType),
                TKCD_PROT_TYPE.getEnum(self.protectionType),
                self.tileSetId, self.panelId, self.cltOpq, keys)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    tileMsg = getBindTileMsg(0xcacacaca, 1, 1, 'P_4x1_32k')
    print tileMsg
    tileMsg = getUnbdTileMsg(0xcacacaca, 1, 1, 'P_4x1_32k__1x2')
    print tileMsg
    print sizeof(tileMsg)


