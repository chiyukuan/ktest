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

class TcsTkcdIo(TestSet):

    def __init__(self, scope='full', ioType='write-read'):
        desc = 'Run %s %s-pattern for tkcd' % (scope, ioType)
        super(TcsTkcdIo, self).__init__(desc)

        self.pId     = 1
        self.addrBeg = 0
        self.gdbScheme = None   # None, 'per-io', 'per-pattern'
        if scope.lower() == 'full':
            self.ioSizeRange = range(1, 257)
        else:
            self.ioSizeRange = (1, 2, 4, 8, 16, 32, 64, 128, 256)

        if   ioType == 'write-read':
            self.ioTypeRange = ['write', 'read']
        elif ioType == 'write':
            self.ioTypeRange = ['write']
        else:
            self.ioTypeRange = ['read']

    def _getTestSpecs(self):
        specs = []

        for ioType in self.ioTypeRange:
            for ioSize in self.ioSizeRange:
                if self.gdbScheme == 'per-io':
                    # do the tkcd gdb state check after write/read
                    for addr in [ self.addrBeg + (x * 4096) for x in range(1024) ]:
                        spec = TctIo('%s %dK at addr %d' % (ioType, ioSize * 4, addr),
                                [[ioType, self.pId, addr, ioSize * 4096]])
                        specs.append( spec )
                        # specs.append( kd.tcases.tkcd.tct_gdb.TctGdb() )
                else:
                    # do the tkcd gdb state check after pattern write/read
                    spec = TctIo(
                            '%s %dK' % (ioType, ioSize * 4),
                            ['%s-pattern' % ioType, self.pId, ioSize * 4096, 
                            self.addrBeg, 4096,
                            None, 1024])
                    specs.append( spec )
                    if bool( self.gdbScheme ):
                        specs.append( kd.tcases.tkcd.tct_gdb.TctGdb() )

        return specs
