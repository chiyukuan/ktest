#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
from kd.util.logger import getLogger
from kd.tcases.tkcd.tct_base import TctBase, DEV_CMD
from kd.tcases.tc_base import TcBase

logger = getLogger(__name__)

class TctDevice(TctBase):

    def __init__(self, cmd='add', wlist=None, params=None):

        self.cmd = cmd.lower()
        if self.cmd == 'add':
            super(TctDevice, self).__init__("Add %s raw disks" % (
                    "all" if wlist is None else wlist))
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep_cfgDevice(DEV_CMD.ADD, wlist=wlist)

        elif self.cmd == 'del':
            super(TctDevice, self).__init__("Del %s raw disks" % (
                    "all" if wlist is None else wlist))
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep_cfgDevice(DEV_CMD.DEL, wlist=wlist)
            # self.addStep("Keep session alive", self._keepSess, opq=params)

        elif self.cmd == 'err-io':
            super(TctDevice, self).__init__("ErrIO %s raw disks" % (
                    "all" if wlist is None else wlist))
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep_cfgDevice(DEV_CMD.ERR_IO, wlist=wlist, ePol=params)

        elif self.cmd == 'err':
            super(TctDevice, self).__init__("Err %s raw disks" % (
                    "all" if wlist is None else wlist))
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep_cfgDevice(DEV_CMD.ERR, wlist=wlist)

    def _tearDown(self, step):
        if self.cmd != 'del':
            super(TctDevice, self)._tearDown(step)

    @classmethod
    def allTestCases(cls):
        tcases = []
        tcases.append( cls() )
        return tcases

    def _keepSess(self, step):
        waitTimeMax = step.opq
        if waitTimeMax is None:
            while True:
                time.sleep( 10 )
        else:
            waitTime = 0
            while waitTime < waitTimeMax:
                time.sleep( 10 )
                waitTime += 10

            

