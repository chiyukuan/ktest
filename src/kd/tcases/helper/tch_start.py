#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Test case helper to stop and start process

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import os
import subprocess, signal
import time
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper
from kd.tcases.tc_bench import TcBench
from kd.tcases.tc_base import TcBase

logger = getLogger(__name__)

class TchStart(TcBase):

    def __init__(self, stopList, startList):
        if bool(stopList) and bool(startList):
            desc = 'stop %s and start %s processes' % (stopList, startList)
        elif bool(stopList):
            desc = 'stop %s processes' % (stopList)
        else:
            desc = 'start %s processes' % (startList)

        super(TchStart, self).__init__(desc)

        self.stopList   = stopList
        self.startList  = startList

        # /opt/Kodiak/
        workdir = TestCase.getParam( 'workdir')
        if workdir is None:
            self.tkcdImg = '/opt/Kodiak/bin/kdtkcd'
        else:
            self.tkcdImg = '%s/usr/src/kdtkd/kdtkcd/OBJS/kdtkcd' % workdir

        if bool(self.stopList):
            self.addStep("Stop process",  self._stopProcess)

        if bool(self.startList):
            self.addStep("Start process", self._startProcess)

    @classmethod
    def allTestCases(cls):
        return []

    def _prepare(self, step):
        super(TchStart, self)._prepare(step, localHost=True)

        if not step.canContinue():
            return

    def _tearDown(self, step):
        step.setRC(RC.OK)

    def _stopProcess(self, step):
        p = subprocess.Popen(['ps', '-A', '-o', 'pid,tty,bsdtime,command'], stdout=subprocess.PIPE)
        out, err = p.communicate()
        for item in self.stopList:
            if item.lower() == 'kdtkd':
                item = 'node ./bin/main kdtkd'
            for line in out.splitlines():
                if item in line and 'attach_gdb.sh' not in line:
                    pid = int(line.split(None, 1)[0])
                    os.kill(pid, signal.SIGKILL)
                    print "Stop the process, %d, %s" % (pid, item)
                    logger.info("Stop the process %s", item)
        step.setRC(RC.OK)

    def _startProcess(self, step):
        for host in self.bench.getDockHosts():

            self.local.run('/usr/sbin/logrotate --force /etc/logrotate.d/kodiak')
            self.local.run('echo "" > ~/nohup.out') ;
            for node in host.nodes:

                for item in self.startList:
                    spec = item.split(".")
                    if spec[0].lower() == 'kdtkcd':
                        if len(spec) == 2:
                            if node.nodeId != int(spec[1]):
                                continue
                        self.local.run('echo "" > ~/nohup.out.%d' % node.nodeId) ;
                        self.local.run("mkdir -p /kodiak/dock/%s/docknode/%d/cfg" % \
                                (self.bench.dockName, node.nodeId) )

                        cmd = "PORT=%d KD_OPT='-d %s -i %d -o %d -n kdtkcd -t %s' " \
                              "nohup %s -D 7 -S tkcd.%s.%d 2>&1 | tee -a ~/nohup.out 1> ~/nohup.out.%d &" % (
                                node.getTkcdPort(), self.bench.dockName,
                                node.nodeId, node.nodeId,
                                host.ip, self.tkcdImg,
                                self.bench.dockName, node.nodeId,
                                node.nodeId)
                        print "Start process, %s" % cmd
                        os.system(cmd)
                time.sleep(5)

if __name__ == '__main__':
    ''' Test this module here '''


