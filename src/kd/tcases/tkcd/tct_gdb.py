#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tcases.tkcd.tct_base import TctBase
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.ep.ep_ctx import getGdbCtx

logger = getLogger(__name__)

class TctGdb(TctBase):

    def __init__(self, gdbCmd=None):
        super(TctGdb, self).__init__('Check kdtkcd memory state', openTkcdSess=False)

        self.gdbSess = None
        self.gdbCmd  = gdbCmd

        self.addStep("Open gdb", self._openGdb)
        if self.gdbCmd is None:
            self.addStep("Check TX state", self._checkTx)
        elif self.gdbCmd == 'tx_history':
            self.addStep("Dump TX history", self._dumpTxHistory)
        else:
            self.addStep("Execute gdb cmd", self._execCmd)

        self.addStep("Close gdb", self._closeGdb)

    def _openGdb(self, step):
        while True:
            self.local.run("pidof kdtkcd")
            if self.local.getRC() != RC.OK:
                step.setRC(RC.ERROR, "Failed to get Pid of kdtkcd")
                break

            gUrl = Url.fromStr("gdb://localhost/%s?%s" % \
                        (self.bench.binKdtkcd, self.local.getRslt()[0]))
            self.gdbSess = getGdbCtx( gUrl )
            self.gdbSess.run("set confirm off")

            step.setRC(RC.OK)
            break

    def _checkTx(self, step):
        self.gdbSess.run("print sizeof(txCB_t::txCB->txs)/sizeof(txCB_t::txCB->txs[0]) - 1")
        txSize = self.gdbSess.getRslt()
        self.gdbSess.run("print txCB_t::txCB->txFreeList.cnt")
        txSizeCur = self.gdbSess.getRslt()

        self.gdbSess.run("print txCB_t::txCB->dBlkCnt")
        dBlkCnt = self.gdbSess.getRslt()
        self.gdbSess.run("print txCB_t::txCB->dBlkFreeListIdx + 1")
        dBlkCntCur = self.gdbSess.getRslt()

        if txSizeCur != txSize or dBlkCntCur != dBlkCnt:
            step.setRC(RC.ERROR, "Count mismatch, Tx off %d, dBlkCnt off %d" % \
                                (int(txSize) - int(txSizeCur), int(dBlkCnt) - int(dBlkCntCur)) )

    def _dumpTxHistory(self, step):
        self.gdbSess.run("print txCB_t::txCB->getFreeTxIdx")
        idxMax = int(self.gdbSess.getRslt())
        idx = 0
        while idx < idxMax:
            self.gdbSess.run("print txCB_t::txCB->getFreeTxs[%d]->txIdx" % idx)

            logger.info("TX History: GetFree txIdx %s", self.gdbSess.getRslt())
            idx += 1

        self.gdbSess.run("print txCB_t::txCB->putFreeTxIdx")
        idxMax = int(self.gdbSess.getRslt())
        idx = 0
        while idx < idxMax:
            self.gdbSess.run("print txCB_t::txCB->putFreeTxs[%d]->txIdx" % idx)

            logger.info("TX History: PutFree txIdx %s", self.gdbSess.getRslt())
            idx += 1


    def _execCmd(self, step):
        while True:
            self.gdbSess.run(self.gdbCmd)
            print self.gdbSess.getRslt()
            break

    def _closeGdb(self, step):
        self.gdbSess.close()

if __name__ == '__main__':
    ''' Test this module here '''


