#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tcases.tkcd.tct_base import TctBase

logger = getLogger(__name__)

class TctTile(TctBase):

    def __init__(self, tileSpecs, desc=None, force=True, pollute=False):
        if desc is None:
            desc = "bind %d %s tile" % ( len(tileSpecs),
                   "P_none" if len(tileSpecs[0]) == 2 else tileSpecs[0][2] )
                
        super(TctTile, self).__init__(desc)
        
        for tileSpec in tileSpecs:
            
            self.addStep_bindTile(tileSpec, force=force, pollute=pollute)

    @classmethod
    def allTestCases(cls):
        tcases = []
        tileSpecs = ( #panel,  #tile-set,  #protection-type
                      [1,      1,          0],
                      [1,      1,          0],
                    )
        tcases.append( cls('Bind few tiles', tileSpecs) )
        return tcases

if __name__ == '__main__':
    ''' Test this module here '''


