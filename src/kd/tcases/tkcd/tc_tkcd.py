#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper
from kd.tkcd.tkcd_msg import getTkcdAddMsg

logger = getLogger(__name__)

class TcTkcd(TestCase):

    def __init__(self, desc, tkcdUrl, msgSpecs):
        super(TcTkcd, self).__init__(None, desc)
        self.tkcdUrl    = tkcdUrl
        self.msgSpecs   = msgSpecs
        self.msgSpecIdx = 0
        self.epCtx      = None

        for msgSpec in msgSpecs:
            self.addStep( msgSpec[0], self._runTkcdAdminCmd)

    @classmethod
    def allTestCases(cls):
        tcases = []
        tkcdUrl = cls.getParamUrl('tkcd.url')

        msgSpecs = [ #desc,       
                     ["Add tkcd", 'ADD_TKCD', 2, tkcdUrl.hostname, 12016]
                   ]
        testcase = cls("Add a TKCD", tkcdUrl, msgSpecs)
        tcases.append( testcase )
        return tcases

    def _prepare(self, step):
        while True:
            self.epCtx = getTkcdCtx(self.tkcdUrl)
            step.setRC(RC.OK)
            if not step.canContinue():  break

            break
        return

    def _tearDown(self, step):
        if self.epCtx is not None:
            self.epCtx.close()
        return

    def _runTkcdAdminCmd(self, step):
        msgSpec = self.msgSpecs[ self.msgSpecIdx ]
        self.msgSpecIdx += 1
        stepDesc, cmdType, dockNodeId, ip, port = msgSpec

        if (cmdType == 'ADD_TKCD'):
            msg = getTkcdAddMsg(dockNodeId, ip, port)

        TcHelper.runTileCmd(step, self.epCtx, msg)


if __name__ == '__main__':
    ''' Test this module here '''


