#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
from kd.util.logger import getLogger
from kd.tcases.tc_base import TcBase
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.text.stats_colloct import StatsColloct
from kd.text.iometer_icf import IometerIcf
from kd.text.iometer_csv import IometerCsv

logger = getLogger(__name__)

class TcIoIometer(TcBase):


    class Stats(StatsColloct):

        def __init__(self):
            super(TcIoIometer.Stats, self).__init__(
                    ['Access Spec', 'IOPS', 'Bandwidth (MB)', 'RespTime (ms)'])

    def __init__(self, desc='Iometer', runSpec=(100, 0), runTime=[0, 10, 0],
            txSzs=[4 * 1024, 64 * 1024, 128 * 1024, 256 * 1024, 512 * 1024, 1024 * 1024],
            vdisk=True, xfs=False, osio=8, workerPerTarget=1, diskSz=0):

        # for xfs disk test
        # dd if=/dev/random of=aa.tst seek=8192000000 count=1 oflag=direct,seek_bytes
        super(TcIoIometer, self).__init__("%s %s %s" % (
            "XFS" if xfs else "Raw", "VDisk" if vdisk else "Disk", desc))

        #runTime = [0, 1, 0]
        #txSzs   = [  4 * 1024, 1024 * 1024]
        self.runTime = runTime
        self.runSpec = runSpec
        self.txSzs   = txSzs
        self.stats   = TcIoIometer.Stats()
        self.vdisk   = vdisk
        self.xfs     = xfs
        self.osio    = osio
        self.workerPerTarget = workerPerTarget
        self.diskSz64  = diskSz * 1024 * 1024 * 1024

        self.lIcfFNs = []
        self.lCsvFNs = []
        self.rIcfFNs = []
        self.rCsvFNs = []
        for txSz in self.txSzs:
            ts = int(time.time())
            icfFN = 'ktest_iometer_%d_%dKB_%dr_%dRm.icf'  % (ts, txSz / 1024, runSpec[0], runSpec[1])
            csvFN = 'ktest_iometer_%d_%dKB_%drd_%dRm.csv' % (ts, txSz / 1024, runSpec[0], runSpec[1])
            self.lIcfFNs.append('%s/%s' % (TcBase.getWorkDir(), icfFN))
            self.lCsvFNs.append('%s/%s' % (TcBase.getWorkDir(), csvFN))
            self.rIcfFNs.append( icfFN )
            self.rCsvFNs.append( csvFN )

        if self.vdisk:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
        elif self.xfs:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.XFS )
            self.addStep("Touch the data file",  self._touchDataFile)
        else:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )

        self.addStep("Gen iometer icf file",              self._genIometerIcf)

        if ( not bool(TcIoIometer.getParam( 'io.iometer_skip') ) ):
            self.addStep("Run iometer",                       self._run)
            self.addStep("Genetate Disk Performance Matrics", self._report)

    @classmethod
    def allTestCases(cls, vdisk=True, xfs=False, osio=8, workerPerTarget=1, diskSz=0):
        # debug mode
        tcases = []
        #                                           Read %, Random %
        tcases.append( cls('Iometer Random Write',    (  0, 100), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )
        tcases.append( cls('Iometer Random Read',     (100, 100), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )
        tcases.append( cls('Iometer Random r80/w20',  ( 80, 100), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )
        tcases.append( cls('Iometer Random r50/w50',  ( 50, 100), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )

        tcases.append( cls('Iometer Sequential Write',(  0,   0), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )
        tcases.append( cls('Iometer Sequential Read', (100,   0), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )

        tcases.append( cls('Iometer Random Write',    (  0, 100), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )
        tcases.append( cls('Iometer Random Read',     (100, 100), vdisk=vdisk, xfs=xfs, osio=osio, workerPerTarget=workerPerTarget, diskSz=diskSz) )
        return tcases

    def _getHost(self):
        return self.bench.getAppHosts() if self.vdisk else self.bench.getDockHosts()

    def _getDevName(self, dev):
        return "%s [xfs]" % dev.devName if self.xfs else dev.devName.split('/')[-1]

    def _prepare(self, step):
        super(TcIoIometer, self)._prepare(step, appHost=self.vdisk, dockHost=not self.vdisk, winHost=True)

    def _tearDown(self, step):
        super(TcIoIometer, self)._tearDown(step)

    def _touchDataFile(self, step):
        for host in self._getHost():
            for dev in host.devs:
                host.run('/bin/dd if=/kodiak/iobw.tst of=%s/iobw.tst '\
                         'bs=%d seek=%d count=1 oflag=direct,seek_bytes' % (
                         dev.name, 4096, self.diskSz64 - 4096))

    def _genIometerIcf(self, step):
        managers = [(self.winHost.url.hostname.upper(), "", [])]
        for host in self._getHost():
            targets = []
            for dev in host.devs:
                targets.append( [self._getDevName(dev), dev.sz if self.diskSz64 == 0 else self.diskSz64] )

            managers.append( (host.url.hostname, host.ip, targets) )

        for idx in range(len(self.txSzs)):

            icf = IometerIcf( self.runTime, [self.txSzs[idx], self.runSpec[0], self.runSpec[1]],
                                            osio=self.osio, workerPerTarget=self.workerPerTarget)
            icf.write( self.lIcfFNs[idx], managers )

            url = Url.fromUrl(self.winHost.url, protocol='scp', filename=self.rIcfFNs[idx])
            execUrlSess( url, scpFrom=self.lIcfFNs[idx] )

    def _run(self, step):
        for idx in range(len(self.rIcfFNs)):

            for host in self._getHost():
                host.run('pkill dynamo')
                host.run('./dynamo -i %s -m %s &' % (self.bench.winEp.ip, host.ip))


            self.winHost.run('/bin/rm %s' % self.rCsvFNs[idx])
            self.winHost.run('%s /c %s /r %s /t 30' %
                    ('/cygdrive/c/Program\ Files/Iometer.org/Iometer\ 1.1/IOmeter.exe',
                     self.rIcfFNs[idx], self.rCsvFNs[idx]))
            time.sleep(1)

            url = Url.fromUrl(self.winHost.url, protocol='scp', filename=self.rCsvFNs[idx])
            execUrlSess( url, scpTo=self.lCsvFNs[idx] )
            self.winHost.run('/bin/rm %s' % self.rCsvFNs[idx])
            self.winHost.run('/bin/rm %s' % self.rIcfFNs[idx])
            time.sleep(1)


    def _report(self, step):

        for idx in range(len(self.txSzs)):
            csv = IometerCsv( self.lCsvFNs[idx] )

            self.stats.newFeed( '%d K' % (self.txSzs[idx]/1024), [csv.getIOps(), csv.getBW(), csv.getRespTime()])

        self.addNotice(step, self.stats, listItem=False)

if __name__ == '__main__':
    ''' Test this module here '''


