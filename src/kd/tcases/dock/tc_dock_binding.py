#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger          import getLogger
from kd.tcases.tc_base       import TcBase
from kd.text.kd_host_binding import KdHostBinding
from kd.util.rc_msg import RC

logger = getLogger(__name__)

class TcDockBinding(TcBase):

    def __init__(self, desc='Dock host binding', sshTunnel=False):
        super(TcDockBinding, self).__init__(desc)

        self.sshTunnel = sshTunnel
        self.curlCmds = [ ('/tmp/auto_dock_host_binding.xml', 'dockhost', 'post', 'host_binding') ]

        self.addStep("Generate host binding file", self._gen  ) ;
        if self.sshTunnel:
            self.addStep_scpToDockHosts( self.curlCmds )
            self.addStep_doCurlCmds( "Post host binding file", self.curlCmds ) ;
        else:
            self.addStep("Post host binding file",     self._postFromHere ) ;
        self.addStep("Check result",               self._check) ;

    @classmethod
    def allTestCases(cls):
        return [cls() ]

    def _prepare(self, step):
        super(TcDockBinding, self)._prepare(step, dockHost=True, localHost=True)

    def _gen(self, step):
        fname    = self.curlCmds[0][0]
        hbinding = KdHostBinding()
        idx = 0
        for host in self.bench.getDockHosts():
            hbinding.addHost('host%02d' % idx, host.ip, host.mac)
            idx2 = 0
            for node in host.nodes:
                host.run('/usr/sbin/ifconfig -s')

                ifNames = host.getRslt()
                ifs = []
                for ifName in ifNames:
                    host.run('/usr/sbin/ifconfig %s | grep netmask | cut -d" " -f10' % ifName)
                    for line in host.getRspMsg().splitlines():
                        if not line.startswith('/usr/sbin/ifconfig '):
                            ifs.append( ifName )

                difs = ifs[-2:]

                host.run('/usr/sbin/ifconfig %s | grep netmask | cut -d" " -f10' % difs[-1])
                for line in host.getRspMsg().splitlines():
                    if not line.startswith('/usr/sbin/ifconfig '):
                        hbinding.addHost('host%02d_node%02d' % (idx, idx2), ip=line)
                        break

                idx2 += 1

            idx += 1

        idx = 0
        for host in self.bench.getAppHosts():
            hbinding.addHost('apphost%02d' % idx, host.ip)
            idx += 1

        hbinding.write(fname)

    def _postFromHere(self, step):
        fname = self.curlCmds[0][0]
        for host in self.bench.getDockHosts():
            self.local.run('/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                            '-d @%s %s/%s' % (fname, host.getDockHostUrl(), self.curlCmds[0][3]))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break

    def _check(self, step):
        fname    = self.curlCmds[0][0]
        self.local.run('mv %s %s/%s' % (fname, TcBase.getWorkDir(), fname[4:]))
        # check the /kodiak/dockhost/host_binding.cfg
        pass


