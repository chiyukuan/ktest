#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from tc_nomad_base import TcNomadBase
from kd.util.rc_msg import RC
from kd.text.stats_colloct import StatsColloct
from kd.tcases.tc_base  import TcBase

logger = getLogger(__name__)

class TcNomadLtnc(TcNomadBase):

    class Stats(StatsColloct):

        def __init__(self):
            super(TcNomadLtnc.Stats, self).__init__(
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

    def __init__(self, desc,
                       txSzs=[  4 * 1024,   8 * 1024,  16 * 1024,   32 * 1024, 64 * 1024,
                              128 * 1024, 256 * 1024, 512 * 1024, 1024 * 1024],
                       tileWrSz = 100 * 1024 * 1024, appHost=True, xfs=False):
        if appHost:
            super(TcNomadLtnc, self).__init__("VDisk " + desc)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
        elif xfs:
            super(TcNomadLtnc, self).__init__("XFS " + desc)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.XFS )
        else:
            super(TcNomadLtnc, self).__init__("Raw Disk " + desc)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )

        self.txSzs      = txSzs ;
        self.tileWrSz   = tileWrSz
        self.stats      = TcNomadLtnc.Stats()
        self.appHost    = appHost
        self.xfs        = xfs
        # add steps

        self.addStep('First write on new tile',     self._oneWr,  opq=0)
        self.addStep('Second write on same tile',   self._oneWr,  opq=1)
        self.addStep('First read on new tile',      self._oneRd,  opq=2)
        self.addStep('Average write on same tile',  self._tileWr, opq=3)
        self.addStep('Average read on same tile',   self._tileRd, opq=4)
        self.addStep('Generate Latency for first/second/average RW Table', self._genReport)

    @classmethod
    def allTestCases(cls, appHost=True, xfs=False):
        tcases = []
        tcases.append( cls('Measure the IO latency via dd', appHost=appHost, xfs=xfs) )
        return tcases

    def _getHost(self):
        return self.bench.getAppHosts() if self.appHost else self.bench.getDockHosts()

    def _getDevName(self, dev):
        return "%s/iobw.tst " % dev.name if self.xfs else dev.name

    def _prepare(self, step):
        super(TcNomadLtnc, self)._prepare(step, appHost=self.appHost)

    def _tearDown(self, step):
        super(TcNomadLtnc, self)._tearDown(step)

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


