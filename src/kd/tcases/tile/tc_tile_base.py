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

logger = getLogger(__name__)

class TcTileBase(TestCase):

    def __init__(self, desc, tkcdUrl, tileSpecs):
        super(TcTileBase, self).__init__(None, desc)
        self.tkcdUrl = tkcdUrl
        self.tileSpecs = tileSpecs
        self.tileSpecIdx = 0
        self.epCtx    = None

        for rspRC, cmdMsg in tileSpecs:
            self.addStep(cmdMsg.__repr__(), self._runTileCmd)

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
        rspRC, cmdMsg = self.tileSpecs[ self.tileSpecIdx ]
        self.tileSpecIdx += 1

        TcHelper.runTileCmd(step, self.epCtx, cmdMsg)
        cmdCtx = self.epCtx.getCmdCtx() ;
        tileMsg = cmdCtx.rspMsg
        if rspRC == RC.ERROR and tileMsg.rc > 1:
            step.setRC(RC.OK)
        elif rspRC == RC.OK and tileMsg.rc == 1:
            step.setRC(RC.OK, "Tile key 0x%lx" % tileMsg.tKey)
        else:
            step.setRC(RC.ERROR, "Invalid rc %d expected result is %s" % (tileMsg.rc, rspRC))

if __name__ == '__main__':
    ''' Test this module here '''


