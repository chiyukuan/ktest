#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
import sys
import random
from kd.util.logger import getLogger
from kd.tfwk.test_case import TestCase
from kd.util.enum import enum
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.text.kd_res import KdRes
from kd.ep.ep_ctx import getTkcdCtx, getLocalCtx, getGdbCtx
from kd.tcases.tc_helper import TcHelper
from kd.tkcd.dev_msg import getAddDevMsg, getDelDevMsg, getErrDevMsg, getErrDevIoMsg
from kd.tkcd.tile_msg import getBindTileMsg, getDelPanelMsg
from kd.tkcd.sshot_msg import getAddSShotMsg, getDelSShotMsg
from kd.tkcd.io_msg import getRdMsg, getWrMsg, IoMsg
from kd.tcases.tc_bench import TcBench
from kd.tcases.tc_base import TcBase

IO_TYPE = enum('WRITE', 'READ', 'WREAD', 'WRITE_AND_READ')
DEV_CMD = enum('ADD', 'DEL', 'ERR_IO', 'ERR')

logger = getLogger(__name__)

class TctBase(TcBase):

    Tiles = {}

    def __init__(self, desc, tkcdUrl=None, openTkcdSess=True):
        super(TctBase, self).__init__(desc)

        self.dockName = TestCase.getParam( 'dock.name' )
        self.nodeIdx  = -1      # support single host only
        self.openTkcdSess = openTkcdSess

    def _prepare(self, step):
        super(TctBase, self)._prepare(step, dockHost=True, localHost=True, \
                                            tkcdNode=self.openTkcdSess)
        if not step.canContinue():
            return

        return

    def _tearDown(self, step):
        super(TctBase, self)._tearDown(step)

    def _getIoType(self, ioTypeStr):
        name = ioTypeStr.lower()
        self.printData = True if '-print-' in name else False
        if name.startswith('write_and_read') or name.startswith('write-and-read'):
            return IO_TYPE.WRITE_AND_READ
        if name.startswith('write'):
            return IO_TYPE.WRITE
        if name.startswith('wread'):
            return IO_TYPE.WREAD
        if name.startswith('read'):
            return IO_TYPE.READ
        return None

    def _cfgDevice(self, step):
        cmd, wlist, ePol = step.opq
        for host in self.bench.getDockHosts():
            rDiskIdx = 0
            nodeLen = len(host.nodes)
            nodeIdx = -1
            for devIdx, dev in enumerate(host.devs):

                nodeIdx += 1
                if nodeIdx >= nodeLen:
                    nodeIdx = 0
                    rDiskIdx += 1
                if wlist is not None:
                    if isinstance( wlist, int ):
                        if devIdx != wlist:
                            continue
                    else:
                        if devIdx not in wlist:
                            continue


                mPath = '/kodiak/dock/%s/docknode/%d/mnt/%d' % (self.dockName, nodeIdx + 1, rDiskIdx)

                if cmd == DEV_CMD.ADD:
                    host.run("mkdir -p %s" % mPath)
                    host.run("mount -t xfs %s %s" % ( dev.devName, mPath ))

                    devMsg = getAddDevMsg(mPath, dBlocks=52428800)

                elif cmd == DEV_CMD.DEL:
                    devMsg = getDelDevMsg(mPath, dBlocks=52428800)

                elif cmd == DEV_CMD.ERR:
                    devMsg = getErrDevMsg(mPath, dBlocks=52428800)

                elif cmd == DEV_CMD.ERR_IO:
                    devMsg = getErrDevIoMsg(mPath, ePol=ePol)
                else:
                    step.setRC(RC.ERROR, "Command %s is not supported" % cmd)

                host.nodes[ nodeIdx ].tkcdCtx.run(devMsg, tryParse=False)
                step.rcMsg = host.nodes[ nodeIdx ].tkcdCtx.getRcMsg()

    def addStep_cfgDevice(self, cmdType, wlist=None, ePol=None):
        opq  = [cmdType, wlist, ePol]
        desc = '%s all raw disks' % cmdType if wlist is None else '%s %s raw disks' % (cmdType, wlist)
        self.addStep(desc, self._cfgDevice, opq=opq)


    def _getTileMInfo(self, tSetId, pId, nodeId=None):
        tkcdCtx = None
        tKey    = None
        tMInfo  = TctBase.Tiles[ '%d@%d' % (tSetId, pId) ]
        hostIp, rspMsg, keyIdx = tMInfo

        while True:
            if nodeId is not None:
                targetNodeId = nodeId
                break ;
            else:

                keyIdx += 1
                if keyIdx >= rspMsg.tKeyCnt:
                    keyIdx = 0

                if keyIdx == 0:
                    targetNodeId = rspMsg.dNodeId
                    tKey         = rspMsg.tKey
                elif keyIdx == 1:
                    targetNodeId = rspMsg.dNodeId2
                    tKey         = rspMsg.tKey2
                else:
                    targetNodeId = rspMsg.dNodeId3
                    tKey         = rspMsg.tKey3
                tMInfo[2] = keyIdx

            for host in self.bench.getDockHosts():
                if host.ip == hostIp:
                    for node in host.nodes:
                        if targetNodeId == node.nodeId:
                            tkcdCtx = node.tkcdCtx
            if tkcdCtx is not None:
                sys.stdout.write( ', %s' % tkcdCtx.sess.url )
                break

        return [tkcdCtx, tKey]

    def _bindTile(self, step, opq=None):
        if opq is None:
            pId, tSetId, protectionType, force, pollute, bindError = step.opq
        else:
            pId, tSetId, protectionType, force, pollute, bindError = opq

        tMInfoKey = '%d@%d' % (tSetId, pId)
        if tMInfoKey not in TctBase.Tiles or force:
            msg = getBindTileMsg(0xcacaca11, pId, tSetId, protectionType)
            for host in self.bench.getDockHosts():
                self.nodeIdx += 1
                if self.nodeIdx >= len(host.nodes):
                    self.nodeIdx = 0

                node    = host.nodes[ self.nodeIdx ]
                if node.tkcdCtx is None:
                    continue
                tkcdCtx = node.tkcdCtx
                sys.stdout.write( "- %s from %s\n" % (msg, tkcdCtx.sess.url) )
                tkcdCtx.run(msg, tryParse=False)
                sys.stdout.write( "  %s from %s\n" % (
                    tkcdCtx.cmdCtx.rspMsg if tkcdCtx.getRC() == RC.OK else tkcdCtx.getRcMsg(), tkcdCtx.sess.url) )
                if bindError:
                    if tkcdCtx.getRC() == RC.OK:
                        step.setRC( RC.ERROR, "Bind should failed" )
                    break

                else:
                    step.rcMsg = tkcdCtx.getRcMsg()
                    if not step.canContinue():
                        break

                TctBase.Tiles[ tMInfoKey ] = [host.ip, tkcdCtx.cmdCtx.rspMsg, -1]
                if pollute:
                    TctBase.Tiles[ tMInfoKey ][1].tKey += 1
                break

    def addStep_bindTile(self, bindSpec, force=False, pollute=False, error=False):

        if len(bindSpec) == 2:      bindSpec.append('P_none')
        bindSpec.append( force )
        bindSpec.append( pollute )
        bindSpec.append( error )
        self.addStep('Bind Tile tileSet %d@%d pType %s' % (bindSpec[1], bindSpec[0], bindSpec[2]),
                     self._bindTile, opq=bindSpec)


    def _delPanel(self, step, opq=None):
        panelId, pTypeKey = step.opq

        msg = getDelPanelMsg(0xcacaca11, panelId, pTypeKey)
        for host in self.bench.getDockHosts():
            self.nodeIdx += 1
            if self.nodeIdx >= len(host.nodes):
                self.nodeIdx = 0

            node    = host.nodes[ self.nodeIdx ]
            tkcdCtx = node.tkcdCtx
            tkcdCtx.run(msg, tryParse=False)
            step.rcMsg = tkcdCtx.getRcMsg()
            if not step.canContinue():
                break

    def addStep_delPanel(self, panelId, pTypeKey):

        if pTypeKey is None:
            pTypeKey = 'P_none'
        self.addStep('Delete panel %d' % panelId, self._delPanel, opq=(panelId, pTypeKey))

    def _addSnapshot(self, step):
        readonly, panelIds = step.opq
        msg = getAddSShotMsg( 0xcacaca11, readonly, panelIds )
        for host in self.bench.getDockHosts():
            self.nodeIdx += 1
            if self.nodeIdx >= len(host.nodes):
                self.nodeIdx = 0

            node    = host.nodes[ self.nodeIdx ]
            tkcdCtx = node.tkcdCtx
            tkcdCtx.run(msg, tryParse=False)
            step.rcMsg = tkcdCtx.getRcMsg()
            if not step.canContinue():
                break


    def addStep_addSnapshot(self, readonly, panelIds):

        self.addStep('Add snapshot', self._addSnapshot, opq=(readonly, panelIds))


    def _rwData(self, step):
        if len(step.opq) == 5:
            ioType, pId, devAddr, byteCnt, protectionType = step.opq
            expectOK = True
        else:
            ioType, pId, devAddr, byteCnt, protectionType, expectOK = step.opq

        if protectionType == 'P_4x1_32k':
            tSetId = (devAddr >> 32) + 1
            addr = devAddr & 0xffffffff
        else:
            tSetId = (devAddr >> 30) + 1
            addr = devAddr & 0x3fffffff

        while True:

            self._bindTile( step, opq=[pId, tSetId, protectionType, False, False, False] )
            if not step.canContinue():
                break


            if ioType == IO_TYPE.WRITE or ioType == IO_TYPE.WREAD or ioType == IO_TYPE.WRITE_AND_READ:
                self.tkcdCtx, tKey = self._getTileMInfo( tSetId, pId )
                msg = getWrMsg(0xcacacacb, tKey, (addr >> 12), (byteCnt >> 12),
                        panelId=pId)
        
                self.tkcdCtx.run(msg, tryParse=False)
                step.rcMsg = self.tkcdCtx.getRcMsg()
                if expectOK:
                    if not step.canContinue():
                        step.setRC(RC.ERROR, "Write Error. Expect OK") ;
                        break
                else:
                    if step.canContinue():
                        step.setRC(RC.ERROR, "Write OK. Expect Error") ;
                        break

            if ioType == IO_TYPE.READ or ioType == IO_TYPE.WREAD or ioType == IO_TYPE.WRITE_AND_READ:
                self.tkcdCtx, tKey = self._getTileMInfo( tSetId, pId )
                msg = getRdMsg(0xcacacacb, tKey, (addr >> 12), (byteCnt >> 12),
                        panelId=pId)
                self.tkcdCtx.run(msg, tryParse=False)
                step.rcMsg = self.tkcdCtx.getRcMsg()

                if expectOK:
                    if not step.canContinue():
                        step.setRC(RC.ERROR, "Read Error. Expect OK") ;
                        break
                else:
                    if step.canContinue():
                        step.setRC(RC.ERROR, "Read OK. Expect Error") ;
                        break
            step.setRC(RC.OK)
            break


    def addStep_rwData(self, ioSpec):
        if len(ioSpec) == 4: ioSpec.append('P_none')
        if isinstance( ioSpec[0], basestring ):
            ioSpec[0] = self._getIoType( ioSpec[0] )

        ioType, pId, addr, byteCnt, protectionType = ioSpec

        self.addStep('%s %d bytes from %d@%d' % (ioType, byteCnt, addr, pId),
                self._rwData, opq=ioSpec)

    def addStep_rwDataInvalid(self, ioSpec):
        if len(ioSpec) == 4: ioSpec.append('P_none')
        if isinstance( ioSpec[0], basestring ):
            ioSpec[0] = self._getIoType( ioSpec[0] )
        ioSpec.append(False)

        print ioSpec
        ioType, pId, addr, byteCnt, protectionType, expectOK = ioSpec

        self.addStep('%s %d bytes from %d@%d' % (ioType, byteCnt, addr, pId),
                self._rwData, opq=ioSpec)


    def _rwDataPattern(self, step):
        ioType, pId, ioSize, addrBeg, addrIncr, addrEnd, ioCnt, protType = step.opq

        if not bool(ioCnt) :
            addrBegs = range(addrBeg, addrEnd, addrIncr)
        else:
            addrBegs = [addrBeg + (x * addrIncr) for x in range(ioCnt) ]

        ioIdx = 1
        for addr in addrBegs:
            step.opq = [ioType, pId, addr, ioSize, protType]
            ioDesc = "- %3d %5s 0x%02x block from %d:%d:0x%05x" % (
                        ioIdx, ioType, ioSize/4096, pId, addr >> 30, (addr & 0x3fffffff)/4096)
            ioIdx += 1
            print ioDesc,
            logger.info( ioDesc )
            self._rwData( step )
            if self.printData:
                print ": 0x%08x %s" % (addr, ''.join('{:02x}'.format(x) \
                                  for x in self.tkcdCtx.getSess().inBuf[IoMsg.msgSize():IoMsg.msgSize() + 16]))
            else:
                print
            if not step.canContinue():
                return

    def addStep_rwDataPattern(self, ioSpec):
        if len(ioSpec) == 7: ioSpec.append('P_none')

        ioType, pId, ioSize, addrBeg, addrIncr, addrEnd, ioCnt, protType = ioSpec
        if isinstance( ioType, basestring ):
            ioType = self._getIoType( ioSpec[0] )
            ioSpec[0] = ioType

        if not bool(addrIncr):
            addrIncr  = ioSize
            ioSpec[4] = ioSize

        if ioCnt is not None:
            myDesc = 'Pattern %s %dK-byte from %dK@%d incr %dK %d times' % (
                    ioType, ioSize >> 10, addrBeg >> 10, pId, addrIncr >> 10, ioCnt )
        else:
            myDesc = 'Pattern %s %dK-byte from %dK@%d to %dK incr %dK' % (
                    ioType, ioSize >> 10, addrBeg >> 10, pId, addrEnd >> 10, addrIncr >> 10)

        self.addStep(myDesc, self._rwDataPattern, opq=ioSpec) 

    def _rwDataRandom(self, step):
        ioType, pId, addrBeg, addrEnd, ioSizeMin, ioSizeMax, ioCnt, protType = step.opq
        random.seed()
        ioIdx = 0 ;

        if ioType == IO_TYPE.WRITE_AND_READ:
            ioTypes = [ IO_TYPE.WRITE, IO_TYPE.READ ]
        else:
            ioTypes = [ ioType ]

        for ioType in ioTypes:
            while (ioIdx < ioCnt):

                ioSize = random.randint(ioSizeMin, ioSizeMax)
                ioSize = ioSize >> 12 << 12

                addr = random.randint(addrBeg, addrEnd - ioSize)
                addr = addr >> 12 << 12

                step.opq = [ioType, pId, addr, ioSize, protType]
                ioDesc = "- %3d %5s %4d KB at offset %8d KB panel-%d" % (
                        ioIdx+1, ioType, ioSize/1024, addr/1024, pId)
                print ioDesc
                logger.info( ioDesc )
                self._rwData( step )
                if not step.canContinue():
                    return
                ioIdx += 1

    def addStep_rwDataRandom(self, ioSpec):
        if len(ioSpec) == 7: ioSpec.append('P_none')
        ioType, pId, addrBeg, addrEnd, ioSizeMin, ioSizeMax, ioCnt, protType = ioSpec
        if isinstance( ioType, basestring ):
            ioSpec[0] = self._getIoType( ioSpec[0] )
            ioType = ioSpec[0]

        myDesc = 'Random %s addr-range [%dK - %dK)@%d ioSize-range [%dK - %dK] %d times' % (
                 ioType, addrBeg >> 10, addrEnd >> 10, pId,
                 ioSizeMin >> 10, ioSizeMax >> 10, ioCnt )

        self.addStep(myDesc, self._rwDataRandom, opq=ioSpec)

    def _rwDataCorner(self, step):
        ioType, pId, addrBeg, protType = step.opq

        specs = [ ('a full stripe',                               1024 * 1024, (          128) * 1024),
                  ('a full stripe + 16K at end',                  1024 * 1024, (     128 + 16) * 1024),
                  ('a full stripe + 64K at end',                  1024 * 1024, (     128 + 64) * 1024),
                  ('a full stripe + 16K at beg',           (1024 - 16) * 1024, (     128 + 16) * 1024),
                  ('a full stripe + 64K at beg',           (1024 - 64) * 1024, (     128 + 64) * 1024),
                  ('a full stripe + 64K at begin and end', (1024 - 64) * 1024, (64 + 128 + 64) * 1024),
                  ('inside one stripe',                              4 * 1024, (            8) * 1024),
                  ('at the boundary of 2 stripes',         (128 +32-4) * 1024, (       4 +  4) * 1024),
                  ('cross 3 stripes',                      ( 64 -  16) * 1024, ( 16 + 32 + 16) * 1024),
                  ('cause cTX use the memory 2 blocks',    (        4) * 1024, ( (60 + 4)+  4) * 1024),
                  ('at the boundary of 2 full-stripes',    (128+64-16) * 1024, ( (64 +16)+ 16) * 1024),
                  ('cross 3 full-stripes',                 (128   - 4) * 1024, (  4 + 128 + 4) * 1024),
                  ('cross multiple full-stripes',          (        4) * 1024, (124 + 256+124) * 1024),
                ]

        if ioType == IO_TYPE.WRITE_AND_READ:
            ioTypes = [ IO_TYPE.WRITE, IO_TYPE.READ ]
        else:
            ioTypes = [ ioType ]

        ioIdx = 1
        for ioType in ioTypes:
            for spec in specs:
                ioSize = spec[2]
                addr   = spec[1] + addrBeg
                ioDesc = "- %3d %5s %4d KB at offset %8d KB panel-%d" % (
                        ioIdx, ioType, ioSize/1024, addr/1024, pId)
                print ioDesc
                logger.info( ioDesc )
                step.opq = [ioType, pId, addr, ioSize, protType]
                self._rwData( step )
                if not step.canContinue():
                    return
                ioIdx += 1


    def addStep_rwDataCorner(self, ioSpec):
        if len(ioSpec) == 2: ioSpec.append(0)
        if len(ioSpec) == 3: ioSpec.append('P_none')

        ioType, pId, addrBeg, protType = ioSpec
        if isinstance( ioType, basestring ):
            ioSpec[0] = self._getIoType( ioSpec[0] )
            ioType = ioSpec[0]

        myDesc = 'Corner %s at %s tile' % (ioType, protType)
        self.addStep(myDesc, self._rwDataCorner, opq=ioSpec)

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

