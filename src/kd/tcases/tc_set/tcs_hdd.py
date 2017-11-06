#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tfwk.test_set import TestSet
from kd.tcases.tkcd.tct_io import TctIo
import kd.tcases

logger = getLogger(__name__)

class TcsHdd(TestSet):

    def __init__(self, xfs=False, scheduler='noop', osio=8, diskSz=80, runtime=[0, 10, 0]):
        desc = 'HDD %s Disk Performance, %d GB disk with %d osio and %s scheduler duration %d:%d:%d' % (
                "xfs" if xfs else "raw", diskSz, osio, scheduler, runtime[0], runtime[1], runtime[2])
        super(TcsHdd, self).__init__(desc)
        self.xfs     = xfs
        self.scheduler = scheduler
        self.osio      = osio
        self.diskSz    = diskSz
        self.runtime   = runtime

    def _getTestSpecs(self):
        specs = []

        specs.append( kd.tcases.helper.tch_dhost.TchDhost('stop') )
        specs.append( kd.tcases.helper.tch_dhost.TchDhost('umount') )

        for diskCnt in [1, 2, 8]:
            specs.append( kd.tcases.helper.tch_dhost.TchDhost('pdev-max', diskCnt) )
            specs.append( kd.tcases.helper.tch_dhost.TchDhost('set-io-scheduler', self.scheduler) )

            for segCnt in [1, 2, 4, 8]:
                for txSz in [128*1024, 1024*1024]:
                    spec = kd.tcases.io.tc_io_iometer.TcIoIometer(
                            '%d disk seq WR %d disk seg' % (diskCnt, segCnt),
                            (  0,   0), self.runtime, [txSz], vdisk=False, xfs=self.xfs,
                            osio=self.osio / segCnt, workerPerTarget = segCnt, diskSz=self.diskSz)
                    specs.append( spec )
                    specs.append( kd.tcases.helper.tch_util.TchUtil('sleep', 60) )

                for txSz in [128*1024, 1024*1024]:
                    spec = kd.tcases.io.tc_io_iometer.TcIoIometer(
                            '%d disk seq RD %d disk seg' % (diskCnt, segCnt),
                            (100,   0), self.runtime, [txSz], vdisk=False, xfs=self.xfs,
                            osio=self.osio / segCnt, workerPerTarget = segCnt, diskSz=self.diskSz)
                    specs.append( spec )
                    specs.append( kd.tcases.helper.tch_util.TchUtil('sleep', 60) )

            #for txSz in [128*1024, 256*1024, 512*1024, 1024*1024]:
            for txSz in [128*1024, 1024*1024]:
                spec = kd.tcases.io.tc_io_iometer.TcIoIometer(
                        '%d disk random WR' % diskCnt,
                        (  0, 100), self.runtime, [txSz], vdisk=False, xfs=self.xfs,
                        osio=self.osio, diskSz=self.diskSz)
                specs.append( spec )
                specs.append( kd.tcases.helper.tch_util.TchUtil('sleep', 60) )

            #for txSz in [128*1024, 256*1024, 512*1024, 1024*1024]:
            for txSz in [128*1024, 1024*1024]:
                spec = kd.tcases.io.tc_io_iometer.TcIoIometer(
                        '%d disk random RD' % diskCnt,
                        (100, 100), self.runtime, [txSz], vdisk=False, xfs=self.xfs,
                        osio=self.osio, diskSz=self.diskSz)
                specs.append( spec )
                specs.append( kd.tcases.helper.tch_util.TchUtil('sleep', 60) )
        return specs


