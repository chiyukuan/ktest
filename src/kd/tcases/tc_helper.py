#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Helper class provides the helper function for testcase class

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import time
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.tkcd.dev_msg import getAddDevMsg
from kd.tkcd.tile_msg import getBindTileMsg, getUnbdTileMsg

logger = getLogger(__name__)

class TcHelper(object):

    def __init__(self):
        pass

    @staticmethod
    def runDeviceCmd(step, epCtx, devMsg):
        epCtx.run(devMsg, tryParse=False)
        step.rcMsg = epCtx.getRcMsg()

    @staticmethod
    def runTileCmd(step, epCtx, tileMsg):
        epCtx.run(tileMsg, tryParse=False)
        step.rcMsg = epCtx.getRcMsg()

    '''
    @staticmethod
    def runIoCmd(step, epCtx, ioMsg):
        epCtx.run(ioMsg, tryParse=False)
        step.rcMsg = epCtx.getRcMsg()
    '''

    @staticmethod
    def runTkcdAdminCmd(step, epCtx, msg):
        epCtx.run(msg, tryParse=False)
        step.rcMsg = epCtx.getRcMsg()

    @staticmethod
    def waitTill(host, fileName, keyword, sleepTime=10, waitTime=600):
        while True:
            host.run("/bin/egrep --color=never '%s' %s" % (keyword, fileName))
            if host.getRC() == RC.OK:
                break
            waitTime -= sleepTime
            if waitTime < 0:
                break
            time.sleep( sleepTime )

        return host.getRC()

if __name__ == '__main__':
    ''' Test this module here '''


