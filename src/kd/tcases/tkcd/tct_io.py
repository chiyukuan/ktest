#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tcases.tkcd.tct_base import TctBase, IO_TYPE

logger = getLogger(__name__)

class TctIo(TctBase):

    def __init__(self, desc, ioSpec):
        if bool(desc):
            super(TctIo, self).__init__(desc)
        else:
            super(TctIo, self).__init__(ioSpec[0])

        if ioSpec[0].lower().endswith('pattern'):
            self.addStep_rwDataPattern(ioSpec)
        elif ioSpec[0].lower().endswith('random'):
            # ioSpec: ioType, pId, addrBeg, addrEnd,
            #         ioSizeMin, ioSizeMax, ioCnt, protType
            self.addStep_rwDataRandom(ioSpec)
        elif ioSpec[0].lower().endswith('corner'):
            self.addStep_rwDataCorner(ioSpec)
        elif ioSpec[0].lower().endswith('invalid'):
            self.addStep_rwDataInvalid(ioSpec)
        else:
            self.addStep_rwData(ioSpec)

    @classmethod
    def allTestCases(cls):
        tcases = []
        ioSpecs = [ #type,          #panel, #addr,  #size, #protection
                    ['write',      1,     0,   4096],
                  ]
        tcases.append( cls( "One Write and one read", ioSpecs ) )

        return tcases
