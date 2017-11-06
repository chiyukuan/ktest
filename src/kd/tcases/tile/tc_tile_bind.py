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
from tc_tile_base     import TcTileBase

logger = getLogger(__name__)

class TcTileBind(TcTileBase):

    def __init__(self, desc, tkcdUrl, tileSpecs):
        super(TcTileBind, self).__init__(desc, tkcdUrl, tileSpecs)

    @classmethod
    def allTestCases(cls):
        tkcdUrl = cls.getParamUrl('tkcd.url')
        tcases = []

        # bind one tile
        tileSpecs = [ # RC,      msg
                      [ RC.OK   ,getBindTileMsg(0xcacacaca, 1, 1, 1) ],
                    ]
        tcases.append( cls( "Add one tile", tkcdUrl, tileSpecs) )

        # bind 10 tile at same panel id
        tileSpecs = []
        for tileSetId in range(10, 10 + 128):
            tileSpecs.append( [ RC.OK,   getBindTileMsg(0xcacacaca, 2, tileSetId, 1) ] )

        tcases.append( cls( "Add 10 tiles in one panel", tkcdUrl, tileSpecs) )

        # bind 10 tile at same tile-set id
        tileSpecs = []
        for panelId in range(20, 30):
            tileSpecs.append( [ RC.OK,   getBindTileMsg(0xcacacaca, panelId, 20, 1) ] )
        tcases.append( cls( "Add 10 tiles in 10 panel", tkcdUrl, tileSpecs) )

        # tile-set bondary test, using panel id 30
        tileSpecs = [ # RC,      msg
                      [ RC.OK,   getBindTileMsg(0xcacacaca, 30,                1, 1) ],
                      [ RC.OK,   getBindTileMsg(0xcacacaca, 30,                2, 1) ],
                      [ RC.OK,   getBindTileMsg(0xcacacaca, 30, (1024 * 1024) -1, 1) ],
                      [ RC.OK,   getBindTileMsg(0xcacacaca, 30, (1024 * 1024) +0, 1) ],
                      [ RC.ERROR,getBindTileMsg(0xcacacaca, 30,                0, 1) ],
                      [ RC.ERROR,getBindTileMsg(0xcacacaca, 30, (1024 * 1024) +1, 1) ],
                    ]
        tcases.append( cls( "tile-set-id boundary test", tkcdUrl, tileSpecs) )

        return tcases


if __name__ == '__main__':
    ''' Test this module here '''


