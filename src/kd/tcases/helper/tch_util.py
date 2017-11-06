#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
import subprocess
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.tfwk.test_case import TestCase
from kd.tcases.tc_bench import TcBench

logger = getLogger(__name__)

class TchUtil(TestCase):

    def __init__(self, cmd, params=None):
        print cmd
        self.cmd    = cmd.lower()

        if 'set-bench' == cmd or 'set_bench' == cmd or 'set bench' == cmd:
            self.benchName = params
            super(TchUtil, self).__init__(None, 'Set bench to %s' % self.benchName)
            self.addStep("new bench", self._setBench)

        if 'sleep' == cmd:
            self.sleepSec = params
            super(TchUtil, self).__init__(None, 'Sleep %d seconds' % self.sleepSec)
            self.addStep("sleep", self._sleep)

        if 'shell' == cmd:
            self.shellSpec = params
            super(TchUtil, self).__init__(None, 'Run shell command %s' % self.shellSpec)
            self.addStep("run", self._runShell)

    @classmethod
    def allTestCases(cls):
        return None

    def _prepare(self, step):
        return

    def _tearDown(self, step):
        return


    def _setBench(self, step):
        TestCase.setBench( self.benchName )
        bench = TcBench()
        for item in bench.desc:
            self.addNotice( step, '<mark>%s</mark>' % item)
        return

    def _sleep(self, step):
        time.sleep(self.sleepSec)


    def _runShell(self, step):
        p = subprocess.Popen( self.shellSpec, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err is None or err == "":
            step.setRC(RC.OK)
        else:
            step.setRC(RC.ERROR, err)

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


