#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
import logging
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.tfwk.test_case import TestCase
from kd.tcases.tc_bench import TcBench
from kd.text.kd_dcfg import KdDcfg
from kd.text.kd_res import KdRes
from kd.text.kd_kdcd_dnlist import KdKdcdDnlist

logger = getLogger(__name__)

class TchDockCfg(TestCase):

    def __init__(self, desc, dockCfgUrl=None):
        super(TchDockCfg, self).__init__(None, desc)

        self.dockCfgFN  = '/tmp/ktest_dock_cfg.xml'
        self.dockListFN = '/tmp/ktest_registry_tkcd_dnlist.json'
        self.dNodes     = None

        # add steps
        if dockCfgUrl is None:
            self.addStep("Generate dockCfg file",  self._genDockCfgXml) ;
        else:
            self.dockCfgUrl = dockCfgUrl
            self.addStep("Copy dockCfg file",      self._copyDockCfgXml) ;

        self.addStep("Post dockCfg file",          self._postDockCfgXml) ;
        self.addStep("Check dock nodes log file",  self._checkDockNodeLog) ;
        self.addStep("Check active dock nodes",    self._checkDockNode) ;
        self.addStep("Check dock ports",           self._checkDockPort) ;

    @classmethod
    def allTestCases(cls):
        dockCfgUrl   = cls.getParamUrl( 'dockCfg.url' )

        tcases = []
        tcases.append( cls('Dock the configuration', dockCfgUrl) )
        return tcases

    def _prepare(self, step):
        self.bench = TcBench()
        self.bench.openDockHosts(step)
        if not step.canContinue():
            return

        self.bench.openAppHosts(step)
        if not step.canContinue():
            return

    def _tearDown(self, step):
        self.bench.close(step)

    def _genDockCfgXml(self, step):
        dcfg = KdDcfg(self.bench.dockUuid, 'auto_dockCfg')
        for host in self.bench.getDockHosts():
            resFN = '/tmp/auto_%s_resources.cfg' % host
            url = Url.fromUrl(host.url, protocol='scp', filename=self.bench.resourceCfg)
            execUrlSess( url, scpTo=resFN)

            res = KdRes( resFN )
            ifAddrs = []
            for ifname in res.getIFNames():
                host.run('/usr/sbin/ifconfig %s | grep netmask | cut -d" " -f10' %
                            ifname)
                for line in host.getRspMsg().splitlines():
                    if not line.startswith('/usr/sbin/ifconfig '):
                        ifAddrs.append( line )
                        break
            res.setIFAddrs( ifAddrs )
            dcfg.addHost( host.mac, host.ip, res, host.nodes )

        dcfg.write( self.dockCfgFN )
        self.dNodes = dcfg.dNodes
        for host in self.bench.getDockHosts():
            url = Url.fromUrl( host.url, protocol='scp', filename=self.dockCfgFN )
            execUrlSess( url, scpFrom=self.dockCfgFN )

    def _copyDockCfgXml(self, step):
        execUrlSess( Url.fromUrl(self.dockCfgUrl, protocol='scp'),
                     scpTo=self.dockCfgFN )
        for host in self.bench.getDockHosts():
            url = Url.fromUrl( host.url, protocol='scp', filename=self.dockCfgFN )
            execUrlSess( url, scpFrom=self.dockCfgFN )

    def _postDockCfgXml(self, step):
        for host in self.bench.getDockHosts():
            url = 'http://localhost:3000/kodiak/api/dockhost/dockconfig'
            host.run('/bin/curl -X POST -H "Content-Type: application/xml" '\
                     '-d @%s %s' % (self.dockCfgFN, url))

    def _checkDockNodeLog(self, step):
        time.sleep(20)
        for host in self.bench.getDockHosts():
            host.run("/bin/egrep --color=never '%s' -B 7 -A 12 %s" % 
                    ('^(Syntax|Reference)?Error', self.bench.consoleLogDH))
            if host.getRC() == RC.OK:
                step.setRC( RC.ERROR, 'DockNode %s failed' % host)
                self.addNotice(step, host.getRspMsg(), isPre=True )
                return

    def _checkDockNode(self, step):
        bHost = self.bench.getBrokerHost()
        bHost.run('/bin/curl %s/?path=/kdcd/dnList > %s' % (
                bHost.getRegistryUrl(), self.dockListFN))

        url = Url.fromUrl( bHost.url, protocol='scp', filename=self.dockListFN )
        execUrlSess( url, scpTo=self.dockListFN )
        dnListReader = KdKdcdDnlist(self.dockListFN)
        tkcdDNodes = dnListReader.getDNodes()

        if len(tkcdDNodes) != len(self.dNodes):
            step.setRC(RC.ERROR, "The active dock node count mismatch")
            return

        for dNode in self.dNodes:
            tkcdDNode = None
            for dNodeTmp in tkcdDNodes:
                if dNode.nId == dNodeTmp.nId:
                    tkcdDNode = dNodeTmp
                    break
            if tkcdDNode is None:
                step.setRC(RC.ERROR,
                        "Dock Node %d is not in active list" % dNode.nId)
                return

            if dNode != tkcdDNode:
                step.setRC(RC.ERROR,
                        "Dock Node %d configuration mismatch" % dNode.nId)
                return

    def _checkDockPort(self, step):
        time.sleep(20)
        for host in self.bench.getAppHosts():
            host.run("/bin/egrep --color=never '%s' -B 7 -A 12 %s" % 
                    ('^(Syntax|Reference)?Error', self.bench.consoleLogAH))
            if host.getRC() == RC.OK:
                step.setRC( RC.ERROR, 'Dockport %s failed' % host)
                self.addNotice(step, host.getRspMsg, isPre=True )
                return

if __name__ == '__main__':
    ''' Test this module here '''


