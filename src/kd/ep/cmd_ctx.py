#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.rc_msg import RcMsg

logger = getLogger(__name__)

class CmdCtx(object):
    ''' hold command related information '''

    def __init__(self):
        self.cmdMsg = ""
        self.rspMsg = ""
        self.rcMsg  = RcMsg()
        self.rslt   = None
        self.sessType = None

    def setRC(self, rc, msg=None):
        self.rcMsg.rc  = rc
        self.rcMsg.msg = msg

    def __str__(self):
        return "cmdMsg: %s\nrspMsg: %s\n rc: %s\n rslt:%s\n" % (
                self.cmdMsg, self.rspMsg, self.rcMsg, self.rslt)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


