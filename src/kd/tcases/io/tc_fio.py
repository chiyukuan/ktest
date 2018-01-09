#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
from kd.tcases.helper.tch_util import TchUtil
from kd.util.logger import getLogger
from kd.tcases.tc_base import TcBase
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.text.stats_colloct import StatsColloct
from kd.text.fio_cfg import FioCfg
from kd.text.fio_rslt import FioRslt

logger = getLogger(__name__)


class TcFio(TcBase):


    class Stats(StatsColloct):

        def __init__(self):
            super(TcFio.Stats, self).__init__(
                    ['Access Spec', 'IOPS', 'Bandwidth (MB)', 'RespTime (ms)'])

    def __init__(self, desc=None, runSpec=(100, 0), runTime=None,
            txSzs=None, vdisk=True, xfs=False, axfs=False, nvme=False, osio=None, workerPerTarget=1,
            diskCnt=None, diskSz=0, diskSzUnit='GB', ioengine='libaio', bw=None, 
            verify=None, ioStat=None, dryrun=False):

        if txSzs is None:
            #txSzs=[1024 * 1024, 512 * 1024, 256 * 1024, 128 * 1024, 64 * 1024, 32 * 1024, 16 * 1024, 8 * 1024, 4 * 1024]
            txSzs=[4 * 1024, 8 * 1024, 16 * 1024, 32 * 1024, 64 * 1024, 128 * 1024, 256 * 1024, 512 * 1024, 1024 * 1024]

        # read/write/readwrite:70/randread/randwrite/randrw:70
        self.verify   = verify
        self.doVerify = False
        if isinstance( runSpec, basestring ):
            if runSpec.startswith('readwrite'):
                tokens = runSpec.split(':')
                runSpec = ( int(tokens[1]), 0 )
            elif runSpec.startswith('read'):
                runSpec = ( 100, 0 )
            elif runSpec.startswith('write'):
                runSpec = (   0, 0 )
            elif runSpec.startswith('randrw'):
                tokens = runSpec.split(':')
                runSpec = ( int(tokens[1]), 100 )
            elif runSpec.startswith('randread'):
                runSpec = ( 100, 100 )
            elif runSpec.startswith('randwrite'):
                runSpec = (   0, 100 )
            elif runSpec.startswith('verify'):
                runSpec = ( 100, 0 )
                self.doVerify = True
                self.verify   = 'crc32c'

        if desc is None: 
            if   runSpec[0] == 0 and runSpec[1] == 0:
                desc = 'FIO Sequential Write'
            elif runSpec[0] == 100 and runSpec[1] == 0:
                desc = 'FIO verify' if self.doVerify else 'FIO Sequential Read'
            elif runSpec[0] == 0 and runSpec[1] == 100:
                desc = 'FIO Random Write'
            elif runSpec[0] == 100 and runSpec[1] == 100:
                desc = 'FIO Random Read'
            else:
                desc = 'FIO %d%% Random r%d/w%d' % ( runSpec[1], runSpec[0], 100 - runSpec[0] )
        if osio is None:
            osio = 8 

        if xfs:
            desc = "XFS %s %s"      % ("VDisk" if vdisk else "Disk", desc)
        elif axfs:
            desc = "APPHOST_XFS %s %s"      % ("VDisk" if vdisk else "Disk", desc)
        elif nvme:
            desc = "RAW-NVME %s %s" % ("VDisk" if vdisk else "Disk", desc)
        else:
            desc = "RAW-SCSI %s %s" % ("VDisk" if vdisk else "Disk", desc)

        if diskCnt is not None:
            desc = "%d %s" % (diskCnt, desc)

        super(TcFio, self).__init__(desc)

        self.runTime = runTime
        self.runSpec = runSpec
        self.txSzs   = txSzs
        self.stats   = TcFio.Stats()
        self.vdisk   = vdisk
        self.xfs     = xfs
        self.axfs    = axfs
        self.nvme    = nvme
        self.diskCnt = diskCnt
        self.ioStat  = ioStat
        self.osios   = [ osio ] if isinstance( osio, (int, long) ) else osio
        self.workerPerTarget = workerPerTarget
        self.ioengine = ioengine
        self.bw       = bw
        if diskSzUnit == 'GB':
            self.diskSz64  = diskSz * 1024 * 1024 * 1024
        elif diskSzUnit == 'MB':
            self.diskSz64  = diskSz * 1024 * 1024
        else:
            self.diskSz64 = 0

        self.ts = int(time.time())

        if self.vdisk:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
        elif self.xfs:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.XFS )
        elif self.axfs:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.APPHOST_XFS )
        elif self.nvme:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
        else:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )


        self.addStep("Gen fio configuration file",        self._genFioCfg)
        if ( not bool(TcBase.getParam( 'io.fio_skip') ) ):
            self.addStep("Run fio",                           self._run)
            self.addStep("Genetate Disk Performance Matrics", self._report)

    @classmethod
    def allTestCases(cls, vdisk=True, xfs=False, axfs=False, nvme=False, runSpecs=None, runTime=None, txSzs=None, diskSz=0, diskCnt=None, osio=None, waitTime=60, ioStat=None):
        # debug mode
        if runSpecs is None:
            runSpecs = [ 'write', 'read', 'randwrite', 'randread', 'randrw:70' ]

        tcases = []

        for runSpec in runSpecs:
            tcases.append( cls(vdisk=vdisk, xfs=xfs, axfs=axfs, nvme=nvme, runSpec=runSpec, runTime=runTime, txSzs=txSzs, diskSz=diskSz, diskCnt=diskCnt, ioStat=ioStat, osio=osio) )
            tcases.append( TchUtil('sleep', waitTime) ),

        return tcases

    def _getFnPreix(self):

        prefix = '%s_fio_%d_%s' % (self.host.url.hostname, self.ts, self.ioengine)
        if self.diskCnt is not None:
            prefix = '%s_disk_%d' % (prefix, self.diskCnt)

        if isinstance(self.txSz, int):
            prefix = '%s_%dKB' % (prefix, self.txSz / 1024)
        else:
            prefix = '%s_%s'   % (prefix, self.txSz)

        prefix   = '%s_osio_%d' % (prefix, self.osio)
        return prefix

    def _getCfgFn(self, remote):
        cfgFN    = '%s_%drd_%dRm.fio' % (self._getFnPreix(), self.runSpec[0], self.runSpec[1])
        return cfgFN if remote else '%s/%s' % (TcBase.getWorkDir(), cfgFN)

    def _getRsltFn(self, remote):
        rsltFN   = '%s_%drd_%dRm.rslt' % (self._getFnPreix(), self.runSpec[0], self.runSpec[1])
        return rsltFN if remote else '%s/%s' % (TcBase.getWorkDir(), rsltFN)

    def _getIoStatFn(self, remote):
        ioStatFN = '%s_%drd_%dRm.ioStat' % (self._getFnPreix(), self.runSpec[0], self.runSpec[1])
        return ioStatFN if remote else '%s/%s' % (TcBase.getWorkDir(), ioStatFN)

    def _getHost(self):
        return self.bench.getAppHosts() if self.vdisk or self.axfs else self.bench.getDockHosts()

    def _getDevName(self, dev):
        return "%s/iobw.tst" % dev.devName if self.xfs or self.axfs else dev.devName

    def _prepare(self, step):
        super(TcFio, self)._prepare(step, appHost=self.vdisk or self.axfs, dockHost=not self.vdisk)

    def _tearDown(self, step):
        super(TcFio, self)._tearDown(step)

    def _genFioCfg(self, step):
        for self.host in self._getHost():
            devs = []
            devCnt = 0
            for dev in self.host.devs:
                devCnt += 1
                if self.diskCnt is not None and devCnt > self.diskCnt:
                    continue
                devs.append( [self._getDevName(dev), dev.sz if self.diskSz64 == 0 or self.diskSz64 > dev.sz else self.diskSz64] )

            idx = -1 ;
            for self.txSz in self.txSzs:
                for self.osio in self.osios:
                    idx += 1

                    cfg = FioCfg( self.runTime, [self.txSz, self.runSpec[0], self.runSpec[1]],
                                            osio=self.osio, workerPerTarget=self.workerPerTarget,
                                            ioengine=self.ioengine, bw=self.bw, verify=self.verify,
                                            doVerify=self.doVerify)
                    cfg.write( self._getCfgFn(False), devs )

                    if bool(TcBase.getParam( 'io.fio_skip' )):
                            continue

                    url = Url.fromUrl(self.host.url, protocol='scp', filename=self._getCfgFn(True))
                    execUrlSess( url, scpFrom=self._getCfgFn(False) )

    def _run(self, step):
        for self.txSz in self.txSzs:
            for self.osio in self.osios:
                for self.host in self._getHost():
                    if self.ioStat is not None:
                        self.host.run('iostat -z -x %d > %s&' % (self.ioStat, self._getIoStatFn(True)) )
                        self.host.run('echo "kill $!" > iostat_kill.sh')

                    #self.host.run('fio ~/%s --output=%s' % (self._getCfgFn(True), self._getRsltFn(True)))
                    self.host.run('fio ~/%s --output=%s' % (self._getCfgFn(True), self._getRsltFn(True)), background=True)

                time.sleep( 5 )
                isCmdRunning = True
                while isCmdRunning:

                    isCmdRunning = False
                    for self.host in self._getHost():
                        if self.host.isCmdRunning():
                            time.sleep( 5 )
                            isCmdRunning = True
                            break

                time.sleep( 5 )
                for self.host in self._getHost():

                    if self.ioStat is not None:
                        self.host.run('/bin/sh iostat_kill.sh')
                        url = Url.fromUrl(self.host.url, protocol='scp', filename=self._getIoStatFn(True))
                        execUrlSess( url, scpTo=self._getIoStatFn(False) )
                        self.host.run('/bin/rm %s' % self._getIoStatFn(True) )

                    url = Url.fromUrl(self.host.url, protocol='scp', filename=self._getRsltFn(True))
                    execUrlSess( url, scpTo=self._getRsltFn(False) )
                    time.sleep(1)
                    self.host.run('/bin/rm %s' % self._getCfgFn(True) )
                    self.host.run('/bin/rm %s' % self._getRsltFn(True))

                    rslt = FioRslt( self._getRsltFn(False) )
                    if self.doVerify:
                        if rslt.errCnt != 0:
                            step.setRC(RC.ERROR, rslt.error )
                            break

                    if isinstance(self.txSz,int):
                        feedKey = '%d K, %d@%s' % (self.txSz/1024, self.osio, self.host.url.hostname)
                    else:
                        feedKey = '%s, %d@%s' % (self.txSz, self.osio, self.host.url.hostname)
                    self.stats.newFeed( feedKey, [rslt.getIOps(), rslt.getBW(), rslt.getRespTime()])

            if not step.canContinue():  break

    def _report(self, step):

        self.addNotice(step, self.stats, listItem=False)

