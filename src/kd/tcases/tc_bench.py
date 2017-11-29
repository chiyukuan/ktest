#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.url import Url
from kd.util.rc_msg import RC
from kd.ep.ep_ctx import getLinuxCtx, getLocalCtx, getTkcdCtx
from kd.tfwk.test_case import TestCase

logger = getLogger(__name__)

class TcBench(object):

    class Dev(object):
        def __init__(self, devName, sz, name, scsiAddr=None):
            self.name     = devName if name is None else name
            self.devName  = devName
            self.sz       = sz
            self.scsiAddr = scsiAddr

        def __str__(self):
            return "%s: %s [%s] %d" % (self.name, self.devName, self.scsiAddr, self.sz)

        __repr__ = __str__

    class DNode(object):
        def __init__(self, nIdx, nodeSpec):
            if nodeSpec is None:
                self.basePort = 5000 + (nIdx * 1000)
                svcSpec       = None

            elif isinstance(nodeSpec, basestring):
                self.basePort = 5000 + (nIdx * 1000)
                svcSpec       = nodeSpec

            else:
                self.basePort = nodeSpec[0]
                svcSpec       = nodeSpec[1]

            self.hasKns       = False
            self.hasPK        = False
            self.hasReflector = False
            self.knsPort      = self.basePort + 1
            self.nodeId       = (nIdx * 16 ) + 1
            self.tkcdCtx      = None
            self.skipClose    = False

            if svcSpec is not None:
                if 'all' in svcSpec:
                    self.hasKns       = True
                    self.hasPK        = True
                    self.hasReflector = True
                else:
                    if 'kns' in svcSpec:
                        self.hasKns = True
                    if 'poolkeeper' in svcSpec:
                        self.hasPK  = True
                    if 'reflector' in svcSpec:
                        self.hasReflector = True

        def serviceNode(self):
            return self.hasKns and self.hasPK and self.hasReflector

        def getTkcdPort(self):
            return self.knsPort + 15

        def getType(self):
            if self.hasKns:
                if self.hasPK:
                    if self.hasReflector:
                        return "svc"
                    else:
                        return "kns_pk"
                else:
                    if self.hasReflector:
                        return "kns_ref"
                    else:
                        return "kns"
            else:
                if self.hasPK:
                    if self.hasReflector:
                        return "pk_ref"
                    else:
                        return "pk"
                else:
                    if self.hasReflector:
                        return "ref"
                    else:
                        return "data"

        def openTkcd(self, step, epIp, checkData, canError=False):
            url = Url.fromStr("tcp://%s:%d/" % (epIp, self.getTkcdPort()) )
            while True:
                if self.tkcdCtx is not None:
                    break

                if checkData:
                    self.tkcdCtx = getTkcdCtx( url )
                else:
                    self.tkcdCtx = getTkcdCtx( url, dFN=None )

                if self.tkcdCtx is None and not canError:
                    step.setRC(RC.ERROR, "Failed to connect to tkcd, %s" % url)
                break

        def close(self, step):
            if self.tkcdCtx is not None and not self.skipClose:
                self.tkcdCtx.close()
                self.tkcdCtx = None

    class Ep(object):

        def __init__(self, host):
            self.urlStr = host['url']
            self.mac    = None if 'mac'   not in host else host['mac']
            self.ip     = None if 'ip'    not in host else host['ip']
            self.hasPK        = False
            self.hasKns       = False
            self.hasReflector = False
            self.knsPort      = None
            self.nodes  = []

            if 'nodes' in host:

                nIdx = 0
                for nodeSpec in host['nodes']:
                    node = TcBench.DNode( nIdx, nodeSpec )
                    self.nodes.append( node )
                    if node.hasKns:
                        self.hasKns = True
                        self.knsPort = node.knsPort

                    if node.hasReflector:
                        self.hasReflector = True

                    if node.hasPK:
                        self.hasPK = True

                    nIdx += 1

            self.url    = Url.fromStr(self.urlStr)
            self.ctx    = None
            self.devs   = None
            self.dIfs   = None
    
        def open(self, step, mesg=True):
            while True:
                if self.ctx is not None:
                    step.setRC(RC.OK)
                    break

                if self.url.hostname in ['localhost', '127.0.0.1']:
                    self.ctx = getLocalCtx()
                else:
                    self.ctx = getLinuxCtx( self.url )

                if self.ctx is None:
                    step.setRC(RC.ERROR, "Failed to open the peer endpoint")
                    break
                
                # option out the all messages
                if mesg:
                    self.run('mesg n')
                break

        def close(self, step):
            if self.ctx is not None:
                self.ctx.close()
                self.ctx = None

        def addDevice(self, devName, sz=None, name=None, scsiAddr=None):
            if self.devs is None:
                self.devs = []

            self.devs.append( TcBench.Dev( devName, sz, name, scsiAddr) )

        def addDIf(self, dIf):
            if self.dIfs is None:
                self.dIfs = []
            self.dIfs.append( dIf )

        def getKnsPort(self):
            return self.knsPort

        def run(self, cmd, timeout=-1):
            self.ctx.run(cmd, timeout=timeout)
            return self.ctx.getRC()

        def getRC(self):
            return self.ctx.getRC()

        def getRcMsg(self):
            return self.ctx.cmdCtx.rcMsg

        def getRspMsg(self):
            return self.ctx.cmdCtx.rspMsg

        def getRslt(self):
            return self.ctx.cmdCtx.rslt

        def getKnsUrl(self):
            return Url.fromUrl(self.url, protocol='http', port=self.knsPort ,
                                         filename='kodiak/api')

        def getRegistryUrl(self):
            return Url.fromUrl(self.url, protocol='http', port=self.knsPort + 2,
                                         filename='kodiak/api/registry')

        def getDockHostUrl(self):
            return Url.fromUrl(self.url, protocol='http', port=3000,
                                         filename='kodiak/api/dockhost')

        def getDockPortUrl(self):
            return Url.fromUrl(self.url, protocol='http', port=3005,
                                         filename='kodiak/api/dockport')

        def getTkcdUrl(self):
            if self.dIfs is None:
                return Url.fromUrl(self.url, protocol='tcp',
                            port=self.knsPort + 15, filename="")
            else:
                return Url.fromUrl(self.url, protocol='tcp', hostname=self.dIfs[0],
                            port=self.knsPort + 15, filename="")

        def debug(self):
            print "htype  '%s'" % self.hType
            print "urlStr '%s'" % self.urlStr
            print "mac    '%s'" % self.mac
            print "ip     '%s'" % self.ip
            print self.nodes

        def __str__(self):
            return self.url.hostname

        __repr__ = __str__


    def __init__(self, bench=None):

        workdir = TestCase.getParam( 'workdir')
        if workdir is None:
            self.binKdtkcd = '/opt/Kodiak/bin/kdtkcd'
        else:
            self.binKdtkcd = '%s/usr/src/kdtkd/kdtkcd/OBJS/kdtkcd' % workdir

        self.debugLog   = '/var/log/kodiak/debug.log'
        self.resourceCfg = '/kodiak/dockhost/resources.cfg'
        self.dockName   = TestCase.getParam( 'dock.name' )
        self.tkRes      = None
        self.placement  = [None, None]
        self.dockEps    = []
        self.appEps     = []
        self.winEp      = None
        self.knsEps     = []
        self.pkEps      = []
        self.buildEp    = None
        self.tkcdCheckData = True
        self.tkcdIgnoreConnErr = False
        lhost = { 'type': 'testrunner',
                  'url' : 'ssh://localhost/'
                }
        self.localEp    = TcBench.Ep( lhost )

        if bench is None:
            bench = TestCase.getParamEval('bench')

        self.desc = bench['desc']

        if 'resource' in bench:
            if 'tk-res' in bench['resource']:
                    self.tkRes = bench['resource']['tk-res']

        if TestCase.hasParam('bench.resource.tk-res'):
            self.tkRes = TestCase.getParamEval('bench.resource.tk-res')

        if TestCase.hasParam('bench.tkcd.checkData'):
            self.tkcdCheckData = TestCase.getParamEval('bench.tkcd.checkData')

        if TestCase.hasParam('bench.tkcd.ignore_conn_err'):
            self.tkcdIgnoreConnErr = TestCase.getParamEval('bench.tkcd.ignore_conn_err')

        if 'placement' in bench:
            self.placement = bench['placement']

        if TestCase.hasParam('bench.placement'):
            self.placement = TestCase.getParamEval('bench.placement')

        if TestCase.hasParam('bench.docknodes'):
            bench['docknodes'] = TestCase.getParamEval('bench.docknodes')

        if 'docknodes' in bench:
            for host in bench['docknodes']:
                if TestCase.hasParam('bench.docknodes.nodes'):
                    host['nodes'] = TestCase.getParamEval( 'bench.docknodes.nodes' )
                ep = TcBench.Ep( host )
                self.dockEps.append( ep )
                if ep.hasKns:
                    self.knsEps.append( ep )
                if ep.hasPK:
                    self.pkEps.append( ep )

        if 'appnodes' in bench:
            for host in bench['appnodes']:
                ep = TcBench.Ep( host )
                self.appEps.append( ep )

        if 'builder' in bench:
            self.buildEp = TcBench.Ep( bench['builder'] )

        if 'windows' in bench:
            self.winEp = TcBench.Ep( bench['windows'] )

    def openDockHosts(self, step):
        for ep in self.dockEps:
            ep.open(step)
            if not step.canContinue():
                return

    def openAppHosts(self, step):
        for ep in self.appEps:
            ep.open(step)
            if not step.canContinue():
                return

    def openBuildHost(self, step):
        self.buildEp.open(step)

    def openKnsHosts(self, step):
        for ep in self.knsEps:
            ep.open(step)
            if not step.canContinue():
                break

    def openWinHost(self, step):
        self.winEp.open(step, mesg=False)

    def openLocalHost(self, step):
        self.localEp.open(step)

    def openTkcdNode(self, step):
        for ep in self.dockEps:
            for node in ep.nodes:
                node.openTkcd(step, ep.ip, self.tkcdCheckData, self.tkcdIgnoreConnErr)
                if not step.canContinue():
                    return

    def close(self, step):
        for ep in self.dockEps:
            for node in ep.nodes:
                node.close(step)
            ep.close(step)

        for ep in self.appEps:
            ep.close(step)

        for ep in (self.buildEp, self.winEp, self.localEp):
            if ep is None:
                continue
            ep.close(step)

    def getDockHosts(self):
        return self.dockEps

    def getAppHosts(self):
        return self.appEps

    def getBuildHost(self):
        return self.buildEp

    def getKnsHosts(self):
        return self.knsEps

    def getKnsHost(self, idx=0):
        return self.knsEps[idx]

    def getWinHost(self):
        return self.winEp

    def getLocalHost(self):
        return self.localEp

    def getDockName(self):
        return self.dockName

    def getKnsAddr(self, idx=0):
        ep = self.knsEps[idx]
        return "%s:%d" % (ep.url.hostname, ep.getKnsPort())

    def getPriKnsAddr(self):
        return getKnsAddr()

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


