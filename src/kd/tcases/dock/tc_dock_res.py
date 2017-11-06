#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.url    import Url
from kd.tcases.tc_base import TcBase
from kd.text.kd_res_xml import KdResXml
from kd.util.kspawn import execUrlSess
from kd.util.rc_msg import RC

logger = getLogger(__name__)

class TcDockRes(TcBase):

    def __init__(self, desc='Dock resource', nvme=False, sshTunnel=False):
        super(TcDockRes, self).__init__(desc)

        self.curlCmds = [ ('/tmp/auto_%s_dock_resources.xml',       'dockhost', 'post', 'resources'),
                          ('/tmp/auto_%s_dock_resources_disks.xml', 'dockhost', 'post', 'resources/disk/device') ]
        if nvme:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
        else:
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
        self.addStep("Generate dockRes file", self._gen  ) ;
        if sshTunnel:
            self.addStep_scpToDockHosts( self.curlCmds )
            self.addStep_doCurlCmds( "Post dockRes file", self.curlCmds ) ;
        else:
            self.addStep("Post dockRes file",     self._postFromHere ) ;
        self.addStep("Check result",          self._check) ;

    @classmethod
    def allTestCases(cls):
        return [cls() ]

    def _prepare(self, step):
        super(TcDockRes, self)._prepare(step, dockHost=True, localHost=True)

    def _gen(self, step):
        for host in self.bench.getDockHosts():
            fname      = self.curlCmds[0][0] % host
            fnameDisks = self.curlCmds[1][0] % host
            resXml     = KdResXml()
            resXmlDisk = KdResXml()

            if bool(host.devs):
                for dev in host.devs:
                    resXmlDisk.addDisk(dev.devName, dev.name)

            host.run('/usr/sbin/ifconfig -s')

            ifNames = host.getRslt()
            ifs = []
            for ifName in ifNames:
                host.run('/usr/sbin/ifconfig %s | grep netmask | cut -d" " -f10' % ifName)
                for line in host.getRspMsg().splitlines():
                    if not line.startswith('/usr/sbin/ifconfig '):
                        ifs.append( ifName )

            resXml.addMgmtIf(ifs[0])

            for ifname in ifs[-1:]:
                resXml.addDataIf(ifname)
            resXml.write(fname)
            resXmlDisk.write(fnameDisks)

    def _postFromHere(self, step):
        for host in self.bench.getDockHosts():
            for curlCmd in self.curlCmds:
                fname = curlCmd[0] % host
                self.local.run('/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                            '-d @%s %s/%s' % (fname, host.getDockHostUrl(), curlCmd[3]))
                if self.local.getRC() != RC.OK:
                    step.setRC(self.local.getRC(), (self.local.getRslt()))
                    break

    def _check(self, step):
        for host in self.bench.getDockHosts():
            fname      = self.curlCmds[0][0] % host
            fnameDisks = self.curlCmds[1][0] % host

            self.local.run('mv %s %s/%s' % (fname,      TcBase.getWorkDir(), fname[4:]))
            self.local.run('mv %s %s/%s' % (fnameDisks, TcBase.getWorkDir(), fnameDisks[4:]))
        pass

