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
            txSzs=None, vdisk=True, xfs=False, nvme=False, osio=None, workerPerTarget=1,
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

        self.lCfgFNs  = []
        self.lRsltFNs = []
        self.lIoStatFNs = []
        self.rCfgFNs  = []
        self.rRsltFNs = []
        self.rIoStatFNs = []
        ts = int(time.time())
        for txSz in self.txSzs:
            for osio in self.osios:
                prefix = 'ktest_fio_%d_%s' % (ts, self.ioengine)
                if self.diskCnt is not None:
                    prefix = '%s_disk_%d' % (prefix, self.diskCnt)

                if isinstance(txSz,int):
                    prefix = '%s_%dKB' % (prefix, txSz / 1024)
                else:
                    prefix = '%s_%s'   % (prefix, txSz)

                prefix   = '%s_osio_%d' % (prefix, osio)
                cfgFN    = '%s_%drd_%dRm.fio'      % (prefix, runSpec[0], runSpec[1])
                rsltFN   = '%s_%drd_%dRm.rslt'     % (prefix, runSpec[0], runSpec[1])
                ioStatFN = '%s_%drd_%dRm.ioStat'   % (prefix, runSpec[0], runSpec[1])


                self.lCfgFNs.append('%s/%s'  % (TcBase.getWorkDir(), cfgFN))
                self.lRsltFNs.append('%s/%s' % (TcBase.getWorkDir(), rsltFN))
                self.lIoStatFNs.append('%s/%s' % (TcBase.getWorkDir(), ioStatFN))
                self.rCfgFNs.append( cfgFN )
                self.rRsltFNs.append( rsltFN )
                self.rIoStatFNs.append( ioStatFN )

        if self.vdisk:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
        elif self.xfs:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.XFS )
        elif self.nvme:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
        else:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )


        if ( not bool(TcBase.getParam( 'io.fio_skip') ) ):
            self.addStep("Gen fio configuration file",        self._genFioCfg)
            self.addStep("Run fio",                           self._run)
            self.addStep("Genetate Disk Performance Matrics", self._report)
            pass

    @classmethod
    def allTestCases(cls, vdisk=True, xfs=False, nvme=False, runSpecs=None, runTime=None, diskSz=0, diskCnt=None, osio=None, waitTime=60, ioStat=None):
        # debug mode
        if runSpecs is None:
            runSpecs = [ 'write', 'read', 'randwrite', 'randread', 'randrw:70' ]

        tcases = []

        for runSpec in runSpecs:
            tcases.append( cls(vdisk=vdisk, xfs=xfs, nvme=nvme, runSpec=runSpec, runTime=runTime, diskSz=diskSz, diskCnt=diskCnt, ioStat=ioStat, osio=osio) )
            tcases.append( TchUtil('sleep', waitTime) ),

        return tcases

    def _getHost(self):
        return self.bench.getAppHosts() if self.vdisk else self.bench.getDockHosts()

    def _getDevName(self, dev):
        return "%s/iobw.tst" % dev.devName if self.xfs else dev.devName

    def _prepare(self, step):
        super(TcFio, self)._prepare(step, appHost=self.vdisk, dockHost=not self.vdisk)

    def _tearDown(self, step):
        super(TcFio, self)._tearDown(step)

    def _genFioCfg(self, step):
        for host in self._getHost():
            devs = []
            devCnt = 0
            for dev in host.devs:
                devCnt += 1
                if self.diskCnt is not None and devCnt > self.diskCnt:
                    continue
                devs.append( [self._getDevName(dev), dev.sz if self.diskSz64 == 0 or self.diskSz64 > dev.sz else self.diskSz64] )

            idx = -1 ;
            for txSz in self.txSzs:
                for osio in self.osios:
                    idx += 1

                    cfg = FioCfg( self.runTime, [txSz, self.runSpec[0], self.runSpec[1]],
                                            osio=osio, workerPerTarget=self.workerPerTarget, ioengine=self.ioengine, bw=self.bw, verify=self.verify, doVerify=self.doVerify)
                    cfg.write( self.lCfgFNs[idx], devs )

                    url = Url.fromUrl(host.url, protocol='scp', filename=self.rCfgFNs[idx])
                    execUrlSess( url, scpFrom=self.lCfgFNs[idx] )

    def _run(self, step):
        for host in self._getHost():
            idx = -1 ;
            for txSz in self.txSzs:
                for osio in self.osios:
                    idx += 1
                    if self.ioStat is not None:
                        host.run('iostat -z -x %d > %s&' % (self.ioStat, self.rIoStatFNs[idx]) )
                        host.run('echo "kill $!" > iostat_kill.sh')

                    host.run('fio ~/%s --output=%s' % (self.rCfgFNs[idx], self.rRsltFNs[idx]))
                    time.sleep(1)

                    if self.ioStat is not None:
                        host.run('/bin/sh iostat_kill.sh')
                        url = Url.fromUrl(host.url, protocol='scp', filename=self.rIoStatFNs[idx])
                        execUrlSess( url, scpTo=self.lIoStatFNs[idx] )
                        host.run('/bin/rm %s' % self.rIoStatFNs[idx] )

                    url = Url.fromUrl(host.url, protocol='scp', filename=self.rRsltFNs[idx])
                    execUrlSess( url, scpTo=self.lRsltFNs[idx] )
                    time.sleep(1)
                    host.run('/bin/rm %s' % self.rCfgFNs[idx] )
                    host.run('/bin/rm %s' % self.rRsltFNs[idx])

                    rslt = FioRslt( self.lRsltFNs[idx] )
                    if self.doVerify:
                        if rslt.errCnt != 0:
                            step.setRC(RC.ERROR, rslt.error )
                            break

                    if isinstance(txSz,int):
                        feedKey = '%d K, %d' % (txSz/1024, osio)
                    else:
                        feedKey = '%s, %d' % (self.txSz, osio)
                    self.stats.newFeed( feedKey, [rslt.getIOps(), rslt.getBW(), rslt.getRespTime()])

            if not step.canContinue():  break

    def _report(self, step):

        self.addNotice(step, self.stats, listItem=False)

