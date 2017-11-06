#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper
from kd.tkcd.dev_msg import getAddDevMsg
from kd.tkcd.tile_msg import getBindTileMsg
from kd.tkcd.io_msg import getWrMsg, getRdMsg
from tc_io_base import IO_TYPE, TcIoBase

logger = getLogger(__name__)

class TcIoLkp(TcIoBase):

    def __init__(self, desc, tkcdUrl, tileInfos, ioSpecs):
        super(TcIoLkp, self).__init__(desc, tkcdUrl, tileInfos, ioSpecs)


    @classmethod
    def allTestCases(cls):
        tcases = []
        tkcdUrl = cls.getParamUrl('tkcd.url')
        tileInfos = [
                        {'msg': getBindTileMsg(0xcacacaca, 100, 1, 1)},
                    ]
        
        lba = 0
        for blocks in [256, 128, 64, 32, 16, 8, 4, 2, 1]:
            # write 64M, tx size <blocks>
            count  = (64 * 256) / blocks
            ioSpecs = [ # desc,                    type,         start, end,  incr,    sz, count
                        ['write %d blocks %d times' % (blocks, count),
                                                   IO_TYPE.WRITE, lba,  -1,blocks,blocks, count],
                      ]
            testcase = cls("write 64M, tx %d blocks, level 1 node collapse" % blocks,
                           tkcdUrl, tileInfos, ioSpecs)
            tcases.append( testcase )
            lba = lba + (64 * 256)

        return tcases

if __name__ == '__main__':
    ''' Test this module here '''


