#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tcases.tc_base import TcBase
from kd.util.rc_msg import RC
from kd.text.stats_colloct import StatsColloct

logger = getLogger(__name__)

class TcIoLtnc(TcBase):

    class Stats(StatsColloct):

        def __init__(self):
            super(TcIoLtnc.Stats, self).__init__(
                    ['Access Spec', '1-WR', '2-WR', 'WR', '1-RD', 'RD'])

        def _genTbl(self):
            for feedSet in self.feedSets:
                cnts = [  0,   0,   0,   0,   0]
                tms  = [0.0, 0.0, 0.0, 0.0, 0.0]
                for feed in feedSet[1:]:
                    # feed = opq, cnt, time
                    cnts[feed[0]] += feed[1]
                    tms [feed[0]] += feed[2]

                row = ['%4d K' % (feedSet[0]/1024)]
                for idx in range(len(tms)):
                    if tms[idx] == 0:
                        row.append( 0 )
                    else:
                        row.append( int(tms[idx] * 1000000) / cnts[idx] )

                self.tbl.append( row )

    def __init__(self, desc=None, vdisk=True, xfs=False, nvme=False,
            txSzs=None, tileWrSz = 100 * 1024 * 1024):

        if txSzs is None:
            txSzs=[  4 * 1024,   8 * 1024,  16 * 1024,   32 * 1024, 64 * 1024,
                   128 * 1024, 256 * 1024, 512 * 1024, 1024 * 1024]
        if desc is None: 
            desc = "Measure latency via dd"

        super(TcIoLtnc, self).__init__(desc)

        self.vdisk      = vdisk
        self.xfs        = xfs
        self.nvme       = nvme
        self.txSzs      = txSzs
        self.tileWrSz   = tileWrSz
        self.stats      = TcIoLtnc.Stats()

        if self.vdisk:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
        elif self.xfs:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.XFS )
        elif self.nvme:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
        else:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )

        self.addStep('First write on new tile',     self._oneWr,  opq=0)
        self.addStep('Second write on same tile',   self._oneWr,  opq=1)
        self.addStep('First read on new tile',      self._oneRd,  opq=2)
        self.addStep('Average write on same tile',  self._tileWr, opq=3)
        self.addStep('Average read on same tile',   self._tileRd, opq=4)
        self.addStep('Generate Latency for first/second/average RW Table', self._genReport)


    @classmethod
    def allTestCases(cls):
        tcases = []
        tcases.append( cls() )
        return tcases

    def _getHost(self):
        return self.bench.getAppHosts() if self.vdisk else self.bench.getDockHosts()

    def _getDevName(self, dev):
        return "%s/iobw.tst"  % dev.devName if self.xfs else dev.devName

    def _prepare(self, step):
        super(TcIoLtnc, self)._prepare(step, appHost=self.vdisk, dockHost=not self.vdisk)

    def _tearDown(self, step):
        super(TcIoLtnc, self)._tearDown(step)

    def _oneWr(self, step):
        for host in self._getHost():
            for dev in host.devs:
                if dev.sz < (len(self.txSzs) + 7) * 1024 * 1024 * 1024:
                    continue
                addr = 1024 * 1024 * 1024
                for bs in self.txSzs:
                    host.run('/bin/dd if=/dev/zero of=%s '\
                             'bs=%d seek=%d count=1 oflag=direct' % (
                             self._getDevName(dev), bs, addr/bs))
                    if bs != host.getRslt()[0]:
                        logger.error("Wrong size") 
                        continue

                    self.stats.newFeed(bs, (step.opq, 1, host.getRslt()[1]))
                    addr += 1024 * 1024 * 1024
        return

    def _oneRd(self, step):
        for host in self._getHost():
            for dev in host.devs:
                if dev.sz < (len(self.txSzs) + 7) * 1024 * 1024 * 1024:
                    continue
                addr = 1024 * 1024 * 1024
                for bs in self.txSzs:
                    host.run('/bin/dd of=/dev/null if=%s '\
                             'bs=%d skip=%d count=1 iflag=direct' % (
                             self._getDevName(dev), bs, addr/bs))
                    if bs != host.getRslt()[0]:
                        logger.error("Wrong size") 

                    self.stats.newFeed(bs, (step.opq, 1, host.getRslt()[1]))
                    addr += 1024 * 1024 * 1024
        return

    def _tileWr(self, step):
        for host in self._getHost():
            for dev in host.devs:
                if dev.sz < (len(self.txSzs) + 7) * 1024 * 1024 * 1024:
                    continue
                addr = 1024 * 1024 * 1024
                for bs in self.txSzs:
                    cnt = self.tileWrSz / bs
                    host.run('/bin/dd if=/dev/zero of=%s '\
                             'bs=%d seek=%d count=%d oflag=direct' % (
                             self._getDevName(dev), bs, addr/bs, cnt))
                    if self.tileWrSz != host.getRslt()[0]:
                        logger.error("Wrong size") 

                    self.stats.newFeed(bs, (step.opq, cnt, host.getRslt()[1]))
                    addr += 1024 * 1024 * 1024
        return

    def _tileRd(self, step):
        for host in self._getHost():
            for dev in host.devs:
                if dev.sz < (len(self.txSzs) + 7) * 1024 * 1024 * 1024:
                    continue
                addr = 1024 * 1024 * 1024
                for bs in self.txSzs:
                    cnt = self.tileWrSz / bs
                    host.run('/bin/dd of=/dev/zero if=%s '\
                             'bs=%d skip=%d count=%d iflag=direct' % (
                             self._getDevName(dev), bs, addr/bs, cnt))
                    if self.tileWrSz != host.getRslt()[0]:
                        logger.error("Wrong size") 

                    self.stats.newFeed(bs, (step.opq, cnt, host.getRslt()[1]))

                    addr += 1024 * 1024 * 1024
        return

    def _genReport(self, step):
        self.addNotice(step, self.stats, listItem=False)
        return


if __name__ == '__main__':
    ''' Test this module here '''



