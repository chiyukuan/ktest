#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
from kd.util.logger import getLogger
from kd.tcases.tc_base import TcBase
from kd.text.kd_dcfg import KdDcfg, KdDHost, KdDNodeTemplate
from kd.util.rc_msg import RC

logger = getLogger(__name__)

class TcDockCfg(TcBase):

    def __init__(self, desc='Dock Configuration', nvme=False, sshTunnel=False):

        super(TcDockCfg, self).__init__(desc)
        self.curlCmds = [('/tmp/auto_dock_config.xml', 'dockhost', 'post', 'dockconfig')]

        self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME if nvme else TcBase.DEV_TYPE.RAW )
        self.addStep("Generate Configuration file", self._gen  ) ;
        if sshTunnel:
            self.addStep_scpToDockHosts( self.curlCmds )
            self.addStep_doCurlCmds( "Post Configuration file", self.curlCmds ) ;
        else:
            self.addStep("Post Configuration file",     self._postFromHere ) ;
        if not sshTunnel:
            #  @todo enable it later
            self.addStep("Check dock nodes log file",   self._checkDockNodeLog) ;
        self.addStep("Check result",                self._check) ;


    @classmethod
    def allTestCases(cls):
        return [cls() ]

    def _prepare(self, step):
        super(TcDockCfg, self)._prepare(step, dockHost=True, localHost=True)

    def _gen(self, step): 
        fname    = self.curlCmds[0][0]
        dcfg = KdDcfg(None, self.bench.dockName)
        if bool(self.bench.tkRes):
            dcfg.tileKeeperRes( self.bench.tkRes )

        print self.bench
        if bool(self.bench.placement):
            dcfg.setPlacement('rack')

        nTmlNames = []
        hIdx = 0
        for host in self.bench.getDockHosts():

            dHost = KdDHost('host%02d' % hIdx)

            nodeCnt = len(host.nodes)
            if host.devs is None:
                devCnt = 0
            else:
                devCnt  = len(host.devs)
            for nodeIdx in range(len(host.nodes)):
                node = host.nodes[nodeIdx]
                if host.devs is None:
                    name = '%s_%d_dev_%d' % (node.getType(), devCnt, nodeCnt)
                else:
                    name = '%s_%d_dev_%d-%d' % (node.getType(), devCnt, nodeCnt, nodeIdx + 1)

                if name not in nTmlNames:
                    nTmlNames.append( name )
                    services = [1 if node.hasKns else None,
                                1 if node.hasPK  else None,
                                1 if node.hasReflector else None]
                    devs = [ host.devs[devIdx].name for devIdx in range(nodeIdx, devCnt, nodeCnt) ]
                    dcfg.addDNodeTml( KdDNodeTemplate( name, 5000, services=services, devices=devs ) )

                dHost.addDNode(name, 'host%02d_node%02d' % (hIdx, nodeIdx), node.basePort)

            dcfg.addDHost( dHost )
            hIdx += 1
        dcfg.write( fname )

    def _postFromHere(self, step):
        for host in self.bench.getDockHosts():
            self.local.run('/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                    '-d @%s %s/%s' % (self.curlCmds[0][0], host.getDockHostUrl(), self.curlCmds[0][3]))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break

    def _checkDockNodeLog(self, step):
        time.sleep(20)
        for host in self.bench.getDockHosts():
            host.run("/bin/egrep --color=never '%s' -B 7 -A 12 %s" % 
                    ('^(Syntax|Reference)?Error', self.bench.debugLog))
            if host.getRC() == RC.OK:
                step.setRC( RC.ERROR, 'DockNode %s failed' % host)
                self.addNotice(step, host.getRspMsg(), isPre=True )
                return

    def _checkDockNode(self, step):
        bHost = self.bench.getKnsHost()
        bHost.run('/bin/curl -L %s/?path=/kdcd/dnList > %s' % (
                bHost.getRegistryUrl(), self.dockListFN))

        url = Url.fromUrl( bHost.url, protocol='scp', filename=self.dockListFN )
        execUrlSess( url, scpTo=self.dockListFN )
        dnListReader = KdKdcdDnlist(self.dockListFN)
        tkcdDNodes = dnListReader.getDNodes()

    def _check(self, step):
        fname    = self.curlCmds[0][0]
        self.local.run('mv %s %s/%s' % (fname, TcBase.getWorkDir(), fname[4:]))
        pass

