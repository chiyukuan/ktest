#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
from kd.util.logger import getLogger
from kd.util.rc_msg import RC, RcMsg

logger = getLogger(__name__)

class Runnable(object):
    ''' runnable object '''

    def __init__(self, tag, desc, method, opq=None):
        ''' method should call setRC before return '''
        self.tag       = "" if tag is None else tag 
        self.desc      = self.__class__.__name__ if desc is None else desc
        self.startTag  = "Not yet"
        self.startTime = 0
        self.endTag    = "Not yet"
        self.endTime   = 0
        self.rcMsg     = RcMsg( RC.NOT_YET, "not yet")
        self.method    = method
        self.skip      = False
        self.opq       = opq
        self.fName     = "%s:%s" % (self.__class__.__module__, self.__class__.__name__)

    def _start(self):
        self.startTime = time.time()
        self.startTag  = time.strftime('%X %x', time.localtime(self.startTime))
        self.setRC(RC.OK)
        if self.method == None:
            logger.info("* -- Start %s testcase, '%s' --", self.fName, self.desc)
        else:
            logger.info("- %s '%s' start", self.tag, self.desc)

    def _end(self):
        self.endTime = time.time()
        self.endTag  = time.strftime('%X %x', time.localtime(self.endTime))
        if self.method == None:
            logger.info("* -- End %s testcase, '%s' --", self.fName, self.desc)
        else:
            logger.info("  %s", self)
    
    def timeDuration(self):
        if self.endTime > self.startTime:
            return "%.1f sec" % (self.endTime - self.startTime)
        else:
            return "%s -- %s" % (self.startTag, self.endTag)

    def nextTag(self, rCnt):
        ''' Generate the new Tag based on the runnable count '''
        if self.tag == "":
            newTag = "%02d" % (rCnt + 2)
        else:
            newTag = "%s.%02d" % (self.tag, rCnt + 2)
        return newTag

    def canContinue(self):
        return self.rcMsg.rc == RC.OK or self.rcMsg.rc == RC.WARNING

    def run(self):
        self._start()
        if (self.method is not None):
            self.method(self)
        self._end()

    def setRcMsg(self, rcMsg):
        self.rcMsg = rcMsg

    def setRC(self, rc, msg=None):
        self.rcMsg.setRC(rc, msg)

    def __str__(self):
        return "%-8s [%s] '%s' start at %s" % (
                self.tag, self.rcMsg, self.desc, self.timeDuration())

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


