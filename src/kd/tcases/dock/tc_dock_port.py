#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tcases.tc_base import TcBase
from kd.text.kd_port import KdPort
from kd.util.rc_msg import RC

logger = getLogger(__name__)

class TcDockPort(TcBase):

    def __init__(self, desc='Dock port'):
        super(TcDockPort, self).__init__(desc)
        self.fname = '%s/auto_dock_port.xml' % TcDockPort.getWorkDir()

        self.addStep("Generate port file", self._gen  ) ;
        self.addStep("Post port file",     self._post ) ;
        self.addStep("Check result",       self._check) ;

    @classmethod
    def allTestCases(cls):
        return [cls() ]

    def _prepare(self, step):
        super(TcDockPort, self)._prepare(step, localHost=True)

    def _gen(self, step):
        kdPort = KdPort()
        for host in self.bench.getKnsHosts():
            for node in host.nodes:
                if not node.hasKns:
                    continue

                kdPort.addKns( self.bench.dockName,
                        "%s:%d" % (host.url.hostname, node.knsPort) )

        kdPort.write(self.fname)

    def _post(self, step):
        for host in self.bench.getAppHosts():
            self.local.run('/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                            '-d @%s %s/resources' % (self.fname, host.getDockPortUrl()))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break


    def _check(self, step):
        pass
