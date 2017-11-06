#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Test long IO.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
from kd.util.logger import getLogger
from kd.util.enum import enum
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper
from kd.tkcd.dev_msg import getAddDevMsg
from kd.tkcd.tile_msg import getBindTileMsg
from kd.tkcd.io_msg import getWrMsg, getRdMsg

IO_TYPE = enum('WRITE', 'READ', 'WRITE_AND_READ')

logger = getLogger(__name__)

class TcIoBase(TestCase):

    def __init__(self, desc, tkcdUrl, tileInfos, ioSpecs):
        ''' ioType: 1: write, 2: read, 3 write and read
        '''
        super(TcIoBase, self).__init__(None, desc)
        self.tkcdUrl     = tkcdUrl
        self.tileInfos   = tileInfos
        self.tileInfoIdx = 0
        self.epCtx       = None
        self.tiles       = []
        self.ioSpecs   = ioSpecs
        self.ioSpecIdx = 0

        for tileInfo in tileInfos:
            self.addStep(tileInfo['msg'].__repr__(), self._runTileCmd)

        for ioSpec in ioSpecs:
            self.addStep( ioSpec[0], self._runPattenIoCmd)

    @classmethod
    def allTestCases(cls):
        return []

    def _prepare(self, step):
        while True:
            self.epCtx = getTkcdCtx(self.tkcdUrl)
            step.setRC(RC.OK)
            if not step.canContinue():  break

            # create device
            for mIdx in range(1, 3):
                dName = '/dev/kodiak/fast-vol-0c2c961c-%d' % mIdx
                mPath = '/kodiak/dock/0011fea2209830/docknode/1/mnt/0/%d' % mIdx

                if not os.path.exists( mPath ):
                    os.makedirs( mPath )

                devMsg = getAddDevMsg(dName, mPath, dBlocks=52428800)
                TcHelper.runDeviceCmd(step, self.epCtx, devMsg)
                if not step.canContinue():  break

            if not step.canContinue():  break

            break
        return

    def _tearDown(self, step):
        if self.epCtx is not None:
            self.epCtx.close()
        return

    def _runTileCmd(self, step):
        tileInfo = self.tileInfos[ self.tileInfoIdx ]
        self.tileInfoIdx += 1
        TcHelper.runTileCmd(step, self.epCtx, tileInfo['msg'])
        cmdCtx = self.epCtx.getCmdCtx() ;
        tileMsg = cmdCtx.rspMsg
        if tileMsg.rc == 1:
            step.setRC(RC.OK, "Tile key 0x%lx" % tileMsg.tKey)
            self.tiles.append( tileMsg )
        else:
            step.setRC(RC.ERROR, "Error code %u" % tileMsg.rc)

    def _runPattenIoCmd(self, step):
        ioSpec = self.ioSpecs[ self.ioSpecIdx ]
        self.ioSpecIdx += 1

        stepDesc, ioType, lbaBeg, lbaEnd, lbaIncr, txSize, txCount  = ioSpec

        ioCount = 0
        if txCount == 0:
            lbaRange = range(lbaBeg, lbaEnd, lbaIncr)
        elif lbaIncr == 0:
            lbaRange = [lbaBeg for x in range(txCount)]
        else:
            lbaRange = [lbaBeg + (x * lbaIncr) for x in range(txCount)]

        for lba in lbaRange:
            tileSetIdBeg = (lba >> 18) + 1
            tileSetIdEnd = ((lba + txSize) >> 18) + 1
            if tileSetIdBeg != tileSetIdEnd:
                continue

            found = False
            for tile in self.tiles:
                if tile.tileSetId == tileSetIdBeg:
                    found = True
                    break ;
            if not found:
                set.setRC( RC.ERROR, "Failed to find the proper tile")
                return

            if ioType == IO_TYPE.READ:
                msg = getRdMsg(0xcacacaca, tile.tKey, lba, txSize)
            else:
                msg = getWrMsg(0xcacacaca, tile.tKey, lba, txSize)

            TcHelper.runIoCmd(step, self.epCtx, msg)
            cmdCtx = self.epCtx.getCmdCtx() ;
            ioMsg = cmdCtx.rspMsg
            if ioMsg.rc != 1:
                step.setRC( RC.ERROR, "error code %u" % ioMsg.rc )
                return

            if ioType == IO_TYPE.WRITE_AND_READ:
                msg = getRdMsg(0xcacacaca, tile.tKey, lba, txSize)
                TcHelper.runIoCmd(step, self.epCtx, msg)
                cmdCtx = self.epCtx.getCmdCtx() ;
                ioMsg = cmdCtx.rspMsg
                if ioMsg.rc != 1:
                    step.setRC( RC.ERROR, "error code %u" % ioMsg.rc )
                    return

            if txCount != 0:
                ioCount += 1
                if (ioCount == txCount):
                    break

        step.setRC( RC.OK )
        return


if __name__ == '__main__':
    ''' Test this module here '''


