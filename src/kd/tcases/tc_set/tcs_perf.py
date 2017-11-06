#! /usr/bin/env python


from kd.tfwk.test_set import TestSet
import kd.tcases

class TcsPerf(object):
    def __init__(self, vdisk=True, xfs=False, nvme=False, runSpecs=None, runTime=None, diskSz=0, diskCnt=None, osio=None, ioStat=None):
        desc = 'FIO xfs, libaio'
        super(TcsPerf, self).__init__(desc)

        self.vdisk    = vdisk
        self.xfs      = xfs
        self.nvme     = nvme
        self.runSpecs = runSpecs
        self.runTime  = runTime
        self.diskSz   = diskSz
        self.diskCnt  = diskCnt
        self.osio     = osio
        self.ioStat   = ioStat

    def _printDesc(self, step):
        pass

    def _getTestSpecs(self):
        specs = []

        specs.append( kd.tcases.helper.tch_dhost.TchDhost('umount') )
        if self.nvme:
            specs.append( kd.tcases.helper.tch_dhost.TchDhost('nvme-format-xfs') )
            specs.append( kd.tcases.helper.tch_dhost.TchDhost('nvme-mount') )

        specs.append( kd.tcases.io.tc_fio.TcFio(vdisk=self.vdisk, xfs=self.xfs, runSpec='write', txSzs=[128*1024], diskSz=self.diskSz, diskCnt=diskCnt) )

        for cnt in range(1, self.diskCnt+1):
            specs.append( kd.tcases.io.tc_fio.TcFio.allTestCases( vdisk=self.vdisk, xfs=self.xfs, nvme=self.nvme, runSpecs=self.runSpecs,
                                    runTime=self.runTime, diskSz=self.diskSz, diskCnt=self.diskCnt, osio=self.osio, ioStat=self.ioStat ) )

              #kd.tcases.io.tc_fio.TcFio(vdisk=False, xfs=True, runSpec='read',txSzs=[ (1 << x) * 1024 for x in range(2, 11) ],runTime=[0,0,30], diskSz=100, diskCnt=1),

              #kd.tcases.io.tc_fio.TcFio(vdisk=False, xfs=True, runSpec='read',  txSzs=[128*1024], runTime=[0,0,30], diskSz=100, diskCnt=1),
              #kd.tcases.io.tc_fio.TcFio(vdisk=False, xfs=True, runSpec='read',  txSzs=[112*1024], runTime=[0,0,30], diskSz=100, diskCnt=1),
              #kd.tcases.io.tc_fio.TcFio(vdisk=False, xfs=True, runSpec='read',  txSzs=[ 96*1024], runTime=[0,0,30], diskSz=100, diskCnt=1),
              #kd.tcases.io.tc_fio.TcFio(vdisk=False, xfs=True, runSpec='read',  txSzs=[ 80*1024], runTime=[0,0,30], diskSz=100, diskCnt=1),
              #kd.tcases.io.tc_fio.TcFio(vdisk=False, xfs=True, runSpec='read',  txSzs=[ 64*1024], runTime=[0,0,30], diskSz=100, diskCnt=1),


        return specs


