#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tfwk.test_set import TestSet
import kd.tcases
import random

logger = getLogger(__name__)

class TcsCtnrMax(TestSet):

    def __init__(self, ctnrMax=4, vdiskMax=64, vdiskSzMax=4 * 1024):
        desc = 'Container Limitation Test, %d container, %d vdisk size %d GB' % (
                ctnrMax, vdiskMax, vdiskSzMax)
        super(TcsCtnrMax, self).__init__(desc)

        # 4 containers, 64 vdisks, and 4TBs.
        self.ctnrMax    = ctnrMax
        self.vdiskMax   = vdiskMax
        self.vdiskAvg   = self.vdiskMax / self.ctnrMax
        self.vdiskSz    = 40
        self.vdiskSzMax = vdiskSzMax
        self.vdiskCnt1  = random.randrange(4, self.vdiskAvg)
        self.vdiskCnt2  = random.randrange(4, self.vdiskAvg)
        self.vdiskCnt3  = random.randrange(4, self.vdiskAvg)
        self.vdiskCnt4  = random.randrange(4, self.vdiskAvg)
        self.phases     = []

        self.phases.append( [(1, random.randrange(4, self.vdiskAvg), self.vdiskSz),
                             (2, random.randrange(4, self.vdiskAvg), self.vdiskSz),
                             (3, random.randrange(4, self.vdiskAvg), self.vdiskSz),
                             (4, random.randrange(4, self.vdiskAvg), self.vdiskSz),
                            ])
        
        self.phases.append( [(1, self.vdiskMax, self.vdiskSz   ) ])
        self.phases.append( [(1,             1, self.vdiskSzMax) ])
        self.phases.append( [(1, self.vdiskAvg, self.vdiskSzMax),
                             (2, self.vdiskAvg, self.vdiskSzMax),
                             (3, self.vdiskAvg, self.vdiskSzMax),
                             (4, self.vdiskAvg, self.vdiskSzMax),
                            ])

        self.addStep('Phase', self._printDesc) 

    def _printDesc(self, step):
        for idx in range(len(self.phases)):
            phase = self.phases[idx]
            vdiskCnt = 0
            for ctnrSpec in phase:
                vdiskCnt += ctnrSpec[1]

            self.addNotice(step,
                    'Phase %d, %d CTNR, %2d x %4dGB vdiskCnt + restart' % (
                        idx, len(phase), vdiskCnt, phase[0][2]))

    def _getTestSpecs(self):
        specs = []

        for idx in range(len(self.phases)):
            phase = self.phases[idx]
            vdiskSz  = 0
            vdiskCnt = 0
            for ctnrSpec in phase:
                vdiskCnt += ctnrSpec[1]

            specs.append(kd.tcases.tc_set.tcs_simple.TcsSimple('restartAndReset'))
            specs.append(kd.tcases.tc_set.tcs_simple.TcsSimple('dockResBindingCfg'))

            for ctnrSpec in phase:
                vdiskSz = ctnrSpec[2]
                specs.append(kd.tcases.dock.tc_dock_ctnr.TcDockCtnr(
                    [ctnrSpec[0], [vdiskSz] * ctnrSpec[1]]))

            specs.append(kd.tcases.nomad.tc_nomad_tile.TcNomadTile(
                'Phase %d, R/W tiles' % idx))
            # reboot with simple traffic
            specs.append(kd.tcases.tc_set.tcs_simple.TcsSimple('restart'))
            if vdiskCnt == self.vdiskMax and vdiskSz == self.vdiskSzMax:
                specs.append( kd.tcases.helper.tch_util.TchUtil('sleep', 30 * 60) )
            else:
                specs.append( kd.tcases.helper.tch_util.TchUtil('sleep',  5 * 60) )


            specs.append(kd.tcases.nomad.tc_nomad_tile.TcNomadTile(
                'Phase %d, R/W tiles after restart' % idx))

        #for spec in specs:
        #    spec.critical = False

        return specs

