#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper
from kd.tkcd.dev_msg import getAddDevMsg
from kd.tkcd.tile_msg import getBindTileMsg
from kd.tkcd.io_msg import getWrMsg, getRdMsg

logger = getLogger(__name__)

class TcIo001(TestCase):

    def __init__(self, desc, tkcdUrl, tileInfos, ioInfos):
        super(TcIo001, self).__init__(None, desc)
        self.tkcdUrl = tkcdUrl
        self.tileInfos = tileInfos
        self.tileInfoIdx = 0
        self.ioInfos = ioInfos
        self.ioInfoIdx = 0
        self.epCtx    = None
        self.tiles    = []

        for tileInfo in tileInfos:
            self.addStep(tileInfo['msg'].__repr__(), self._runTileCmd)

        for ioInfo in ioInfos:
            self.addStep(ioInfo['msg'].__repr__(), self._runIoCmd)


    @classmethod
    def allTestCases(cls):
        tcases = []
        tkcdUrl = cls.getParamUrl('tkcd.url')
        tileInfos = [
                        {'msg': getBindTileMsg(0xcacacaca, 100, 1, 1)},
                    ]
        
        # one write/read
        ioInfos = [ {'msg': getWrMsg(0xcacacacb, 0, 63 * 256, 256), 'panelId':100, 'tileSetId':1},
                    {'msg': getRdMsg(0xcacacaca, 0, 63 * 256, 256), 'panelId':100, 'tileSetId':1} ]

        tcases.append( cls( "One Write and one read", tkcdUrl, tileInfos, ioInfos) )

        # wrong tileSetId
        ioInfos = [ {'msg': getRdMsg(0xcacacaca, 0,       256 * 1024, 1), 'panelId':100, 'tileSetId':1, 'ERROR': True},
                    {'msg': getRdMsg(0xcacacaca, 0x20101,          0, 1), 'panelId':100, 'tileSetId':1, 'ERROR': True} ]

        tcases.append( cls( "One Write and one read", tkcdUrl, tileInfos, ioInfos) )

        ioInfos = [
                {'msg': getWrMsg(0xcacacacb, 0, 64*256 + 1, 1), 'panelId':100, 'tileSetId':1},
                {'msg': getWrMsg(0xcacacacb, 0, 64*256 + 3, 1), 'panelId':100, 'tileSetId':1},
                {'msg': getWrMsg(0xcacacacb, 0, 64*256 + 5, 1), 'panelId':100, 'tileSetId':1},
                {'msg': getRdMsg(0xcacacacb, 0, 64*256 + 0, 256), 'panelId':100, 'tileSetId':1},
                ]
        tcases.append( cls( "Read on not initialized area", tkcdUrl, tileInfos, ioInfos) )


        return tcases

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

                devMsg = getAddDevMsg(dName, mPath)
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

    def _runIoCmd(self, step):
        ioInfo = self.ioInfos[ self.ioInfoIdx ]
        self.ioInfoIdx += 1
        ioCmd = ioInfo['msg']
        if ioCmd.tKey == 0:
            found = False
            for tile in self.tiles:
                if tile.panelId == ioInfo['panelId'] and tile.tileSetId == ioInfo['tileSetId']:

                    found = True
                    break ;
            if not found:
                step.setRC( RC.ERROR, "Failed to find the required tile")
                return
            ioCmd.tKey = tile.tKey

        TcHelper.runIoCmd(step, self.epCtx, ioCmd)
        cmdCtx = self.epCtx.getCmdCtx() ;
        ioMsg = cmdCtx.rspMsg
        if 'ERROR' not in ioInfo or ioInfo['ERROR'] == False:
            if ioMsg.rc == 1:
                step.setRC( RC.OK )
            else:
                step.setRC( RC.ERROR, "error code %u" % ioMsg.rc )
        else:
            if ioMsg.rc == 1:
                step.setRC( RC.ERROR, "This step should failed")
            else:
                step.setRC( RC.OK, "error code %u" % ioMsg.rc )

if __name__ == '__main__':
    ''' Test this module here '''


