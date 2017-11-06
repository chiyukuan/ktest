#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Test device addition

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

logger = getLogger(__name__)
TcDevMNameRoot = '/tmp/dev/kodiak/fast-vol-0c2c961c'
TcDevMPathRoot = '/tmp/kodiak/dock/0011fea2209830/docknode/1/mnt'

class TcDev001(TestCase):

    def __init__(self, desc, tkcdUrl, devSpecs):
        super(TcDev001, self).__init__(None, desc)
        self.tkcdUrl = tkcdUrl
        self.devSpecs = devSpecs
        self.devSpecIdx = 0
        self.epCtx    = None

        for rspRC, cmdMsg in devSpecs:
            self.addStep("%s %s - rslt:%s" % (cmdMsg.getCmdName(), cmdMsg.mPath, rspRC), 
                         self._addDevice) 

    @classmethod
    def allTestCases(cls):
        tkcdUrl = cls.getParamUrl('tkcd.url')
        tcases = []

        # add 1 device
        devSpecs = [ # RC,    msg
                     [ RC.OK, getAddDevMsg(TcDevMNameRoot, TcDevMPathRoot + '/0') ]
                   ]
        tcases.append( cls( "Add one device", tkcdUrl, devSpecs) )

        # add 2 device with mount index 0 and 255
        devSpecs = [ # RC,      msg
                     [ RC.OK,   getAddDevMsg(TcDevMNameRoot + '-tmp100', TcDevMPathRoot + '/100') ],
                     [ RC.OK,   getAddDevMsg(TcDevMNameRoot + '-tmp255', TcDevMPathRoot + '/255') ],
                   ]
        tcases.append( cls( "Add two device", tkcdUrl, devSpecs) )

        # add 2 device with mount index less than 0 or great than 255
        devSpecs = [ # RC,      msg
                     [ RC.ERROR,getAddDevMsg(TcDevMNameRoot + '-tmp256', TcDevMPathRoot + '/256') ],
                     [ RC.ERROR,getAddDevMsg(TcDevMNameRoot + '-tmp-1', TcDevMPathRoot + '/-1') ],
                   ]
        tcases.append( cls( "Add 2 device with 256/-1mIdx", tkcdUrl, devSpecs) )

        # add same device more than one time
        devSpecs = [ # RC,      msg
                     [ RC.OK,   getAddDevMsg(TcDevMNameRoot + '-tmp10', TcDevMPathRoot + '/10') ],
                     [ RC.OK,   getAddDevMsg(TcDevMNameRoot + '-tmp10', TcDevMPathRoot + '/10') ],
                   ]
        tcases.append( cls( "Add same device twice", tkcdUrl, devSpecs) )
        
        # using the same mount index to add two device
        devSpecs = [ # RC,      msg
                     [ RC.OK,   getAddDevMsg(TcDevMNameRoot + '-tmp11-A', TcDevMPathRoot + '/11') ],
                     [ RC.ERROR,getAddDevMsg(TcDevMNameRoot + '-tmp11-B', TcDevMPathRoot + '/11') ],
                   ]
        tcases.append( cls( "Add different device at same mIdx", tkcdUrl, devSpecs) )

        # add unexist device
        devSpecs = [ # RC,      msg
                     [ RC.ERROR,getAddDevMsg(TcDevMNameRoot + '-unexist', TcDevMPathRoot + '/unexist/20') ],
                   ]
        tcases.append( cls( "Add unexisting device", tkcdUrl, devSpecs) )
        # add device when the tkcd is loading device/tile info
        return tcases

    def _prepare(self, step):
        while True:
            if not os.path.exists( TcDevMPathRoot ):
                os.makedirs( TcDevMPathRoot )
            for mIdx in range(256):
                mPath = "%s/%d" % (TcDevMPathRoot, mIdx)
                if not os.path.exists( mPath ):
                    os.makedirs(  mPath )

            self.epCtx = getTkcdCtx(self.tkcdUrl)
            step.setRC(RC.OK)
            break
        return

    def _tearDown(self, step):
        if self.epCtx is not None:
            self.epCtx.close()
        return

    def _addDevice(self, step):
        rspRC, cmdMsg = self.devSpecs[self.devSpecIdx]
        self.devSpecIdx += 1

        TcHelper.runDeviceCmd(step, self.epCtx, cmdMsg)
        cmdCtx = self.epCtx.getCmdCtx() ;
        devMsg = cmdCtx.rspMsg
        if rspRC == RC.ERROR and devMsg.rc > 1:
            step.setRC(RC.OK)
        elif rspRC  == RC.OK and devMsg.rc == 1:
            step.setRC(RC.OK)
        else:
            step.setRC(RC.ERROR, "Invalid rc %d expected result is %s" % (devMsg.rc, rspRC))

            

if __name__ == '__main__':
    ''' Test this module here '''
    tcase = TcDev001()
    tcase.run()


