#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Test device addition

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper
from kd.tkcd.dev_msg import getAddDevMsg

logger = getLogger(__name__)

class TchSetup(TestCase):

    def __init__(self, desc, tkcdUrl, devInfos):
        super(TchSetup, self).__init__(None, desc)
        self.tkcdUrl = tkcdUrl
        self.devInfos = devInfos
        self.devInfoIdx = 0
        self.epCtx    = None

        for devInfo in devInfos:
            self.addStep(devInfo['msg'].__repr__(), self._addDevice) 

    @classmethod
    def allTestCases(cls):
        tkcdUrl = cls.getParamUrl('tkcd.url')
        tkcdUrl = Url.fromStr('tcp://localhost:5017')
        tcases = []
        # add 1 device
        devInfos = [ {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c', '/kodiak/dock/0011fea2209830/docknode/1//mnt/0'),
                      'RC' : RC.OK},
                   ]
        tcases.append( cls( "Add one device", tkcdUrl, devInfos) )
        # add 2 device with mount index 0 and 255
        devInfos = [ {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp100', '/kodiak/dock/0011fea2209830/docknode/1//mnt/100', 15),
                      'RC' : RC.OK},
                     {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp255', '/kodiak/dock/0011fea2209830/docknode/1//mnt/255', 15),
                      'RC' : RC.OK},
                   ]
        tcases.append( cls( "Add two device", tkcdUrl, devInfos) )
        # add 2 device with mount index less than 0 or great than 255
        devInfos = [ {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp256', '/kodiak/dock/0011fea2209830/docknode/1//mnt/256', 15),
                      'RC' : RC.ERROR},
                     {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp-1', '/kodiak/dock/0011fea2209830/docknode/1//mnt/-1', 15),
                      'RC' : RC.ERROR},
                   ]
        tcases.append( cls( "Add 2 device with 256/-1mIdx", tkcdUrl, devInfos) )
        # add same device more than one time
        devInfos = [ {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp10', '/kodiak/dock/0011fea2209830/docknode/1//mnt/10', 15),
                      'RC' : RC.OK},
                     {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp10', '/kodiak/dock/0011fea2209830/docknode/1//mnt/10', 15),
                      'RC' : RC.OK},
                   ]
        tcases.append( cls( "Add same device twice", tkcdUrl, devInfos) )
        
        # using the same mount index to add two device
        devInfos = [ {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp11', '/kodiak/dock/0011fea2209830/docknode/1//mnt/11', 15),
                      'RC' : RC.OK},
                     {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-tmp11-B', '/kodiak/dock/0011fea2209830/docknode/1//mnt/11', 15),
                      'RC' : RC.ERROR},
                   ]
        tcases.append( cls( "Add different device at same mIdx", tkcdUrl, devInfos) )
        # add unexist device
        devInfos = [ {'msg': getAddDevMsg('/dev/kodiak/fast-vol-0c2c961c-unexist', '/kodiak/dock/0011fea2209830/docknode/1//mnt/20'),
                      'RC' : RC.ERROR},
                   ]
        tcases.append( cls( "Add unexisting device", tkcdUrl, devInfos) )
        # add device when the tkcd is loading device/tile info
        return tcases

    def _prepare(self, step):
        while True:
            self.epCtx = getTkcdCtx(self.tkcdUrl)
            step.setRC(RC.OK)
            break
        return

    def _tearDown(self, step):
        if self.epCtx is not None:
            self.epCtx.close()
        return

    def _addDevice(self, step):
        devInfo = self.devInfos[self.devInfoIdx]
        self.devInfoIdx += 1
        TcHelper.runDeviceCmd(step, self.epCtx, devInfo['msg'])
        cmdCtx = self.epCtx.getCmdCtx() ;
        devMsg = cmdCtx.rspMsg
        if devInfo['RC'] == RC.ERROR and devMsg.rc > 1:
            step.setRC(RC.OK)
        elif devInfo['RC'] == RC.OK and devMsg.rc == 1:
            step.setRC(RC.OK)
        else:
            step.setRC(RC.ERROR, "Invalid rc %d expected result is %s" % (devMsg.rc, devInfo['RC']))

            

if __name__ == '__main__':
    ''' Test this module here '''
    tcase = TcDev001()
    tcase.run()


