#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import time
from kd.util.logger import getLogger
from kd.util.enum import enum
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.tfwk.test_case import TestCase
from kd.tcases.tc_bench import TcBench

logger = getLogger(__name__)

class TcBase(TestCase):

    DEV_TYPE = enum('VDISK', 'XFS', 'RAW', 'NVME')

    class CurlCmd(object):
        def __init__(self, fname, service, method, path):
            self.fname   = fname
            self.service = service
            self.method  = method.upper()
            self.path    = path

        def getRemoteFName(self):
            if self.fname is None:
                return None

            if "%s" in fname:
                return "/tmp/%s" % (self.fname % host)

            return "/tmp/%s" % self.fname 

        def getLocalFName(self):
            if self.fname is None:
                return None

            if "%s" in fname:
                return "%s/%s" % (TcBase.getWorkDir(), self.fname % host)

            return "%s/%s" % (TcBase.getWorkDir(), self.fname)

        def getCurlCmd(self, url, fname):

            if self.method == 'GET':
                flags1 = ""
                flags2 = ""
            elif self.method == 'DELETE':
                flags1 = " -L -X"
                flags2 = ""
            else:
                flags1 = " -L -X"
                if fname is None:
                    flags2 = ' -H "Content-Type: application/xml" '
                else:
                    flags2 = ' -H "Content-Type: application/xml" -d @%s' % fname

            return '/bin/curl%s %s%s %/%s' % (flags1, self.method, flags2, url, self.path)

        def copyToRemote(self, host, step):
            url = Url.fromUrl(host.url, protocol='scp', filename=self.getRemoteFName())
            execUrlSess( url, scpFrom=self.getLocalFName() )

        def copyFromRemote(self, step):
            url = Url.fromUrl(host.url, protocol='scp', filename=self.getRemoteFName())
            execUrlSess( url, scpTo=self.getLocalFName() )

        def executeAtRemote(self, host, step):
            if self.service == 'kns':
                url = host.getKnsUrl()
            elif self.service == 'dockhost':
                url = host.getDockHostUrl()
            else:
                logger.error("web service server %s not defined.")

            url.useLocalhost()

            cmd = self.getCurlCmd( url, self.getRemoteFName() )
            
            host.run(cmd)
            if host.getRC() != RC.OK:
                step.setRC(host.getRC(), (host.getRslt()))


    def __init__(self, desc, sleepTime=10, waitTime=600):
        super(TcBase, self).__init__(None, desc)
        self.bench     = None
        self.sleepTime = sleepTime
        self.waitTime  = waitTime

    @classmethod
    def allTestCases(cls):
        return []


    def _prepare(self, step, appHost=False, dockHost=False, localHost=False,
            winHost=False, bHost=False, tkcdNode=False):
        self.bench = TcBench()
        if appHost:
            self.bench.openAppHosts(step)
            if not step.canContinue():  return
        if dockHost:
            self.bench.openDockHosts(step)
            if not step.canContinue():  return
        if localHost:
            self.bench.openLocalHost(step)
            if not step.canContinue():  return
            self.local = self.bench.getLocalHost()
        if winHost:
            self.bench.openWinHost(step)
            if not step.canContinue():  return
            self.winHost = self.bench.getWinHost()
        if bHost:
            self.bench.openBuildHost(step)
            if not step.canContinue():  return
            self.bHost = self.bench.getBuildHost()
        if tkcdNode:
            self.bench.openTkcdNode(step)
            if not step.canContinue():  return


    def _tearDown(self, step):
        self.bench.close(step)

    def _getDeviceList(self, step):
        devType = step.opq
        timeSpend = 0
        if devType == TcBase.DEV_TYPE.VDISK:
            for host in self.bench.getAppHosts():
                # wait till device is available
                while True:
                    if timeSpend > self.waitTime:
                        break
                    host.run('/bin/ls --color=none /dev/kdblk*')
                    if host.getRC() == RC.OK:
                        break
                    timeSpend += self.sleepTime
                    time.sleep( self.sleepTime )

                devs = host.getRslt()
                for dev in devs:
                    host.run('blockdev --getsize64 %s' % dev)
                    host.addDevice( dev, host.getRslt() )

        elif devType == TcBase.DEV_TYPE.XFS:
            for host in self.bench.getDockHosts():
                host.run('/bin/ls --color=none -d /kodiak/dock/%s/docknode/*/mnt/*' %
                        self.bench.dockName)
                devs = host.getRslt()
                for dev in devs:
                    # assume the dev size is 128G. Need a way to know the actual size
                    host.addDevice( dev, 128 * 1024 * 1024 * 1024 )

        elif devType == TcBase.DEV_TYPE.RAW:
            for host in self.bench.getDockHosts():
                host.run('/bin/lsscsi')
                devs = host.getRslt()
                host.run('/usr/sbin/pvdisplay -c')
                pvAttr = host.getRslt()

                idx = 0
                for dev in devs:
                    if dev[0] in pvAttr[0]:
                        continue
                    host.run('blockdev --getsize64 %s' % dev[0])
                    host.addDevice( dev[0], host.getRslt(), "Disk%02d" % idx, dev[1] )
                    idx += 1

        elif devType == TcBase.DEV_TYPE.NVME:
            for host in self.bench.getDockHosts():
                # Debug mode, only use one nvme device
                #host.run('/bin/ls --color=none /dev/nvme0n1')
                host.run('/bin/ls --color=none /dev/nvme[2-9]n1')
                #host.run('/bin/ls --color=none /dev/nvme*n1')
                devs = host.getRslt()

                idx = 0
                for dev in devs:
                    host.run('blockdev --getsize64 %s' % dev)
                    host.addDevice( dev, host.getRslt(), "Disk%02d" % idx )
                    idx += 1

        else:
            step.setRC(RC.ERROR, "Failed to identify the dev type %s" % devType)


    def addStep_getDeviceList(self, devType):
        self.addStep("Get %s device list" % devType,
                self._getDeviceList, opq=devType)

    def _getIfList(self, step):
        for host in self.bench.getDockHosts():
            host.run('/usr/sbin/ifconfig -s')
            difs = host.getRslt()[-2:]

            host.run('/usr/sbin/ifconfig %s | grep netmask | ' \
                     'cut -d" " -f10' % difs[0])
            for line in host.getRspMsg().splitlines():
                if not line.startswith('/usr/sbin/ifconfig '):
                    host.addDIf( line )

    def addStep_getIfList(self, devType):
        self.addStep("Get interface list", self._getIfList)

    def _scpToDockHosts(self, step):
        for host in self.bench.getDockHosts():
            for pair in step.opq:
                if pair[0] is None:
                    continue
                fname = pair[0] % host if "%s" in pair[0] else pair[0]
                url   = Url.fromUrl(host.url, protocol='scp', filename=fname)
                execUrlSess( url, scpFrom=fname )

    def addStep_scpToDockHosts(self, pairs):
        self.addStep("Scp files to dock host", self._scpToDockHosts, opq=pairs)

    def _doCurlCmds(self, step):
        curlCmds = step.opq
        for host in self.bench.getDockHosts():
            for curlCmd in curlCmds:
                print curlCmd
                fname, svr, method, path = curlCmd
                if fname is not None and "%s" in fname:
                    fname = fname % host

                if svr == 'kns':
                    url = host.getKnsUrl()
                elif svr == 'dockhost':
                    url = host.getDockHostUrl()
                else:
                    logger.error("web service server %s not defined.")

                url.useLocalhost()

                if method == 'post':
                    cmd = '/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                          '-d @%s %s/%s' % (fname, url, path)
                elif method == 'put':
                    cmd = '/bin/curl -L -X PUT -H "Content-Type: application/xml" '\
                          '%s/%s' % (url, path)
                else:
                    cmd = None

                host.run(cmd)
                if host.getRC() != RC.OK:
                    step.setRC(host.getRC(), (host.getRslt()))
                    break

    def addStep_doCurlCmds(self, stepDesc, curlCmds):
        self.addStep(stepDesc, self._doCurlCmds, opq=curlCmds)

if __name__ == '__main__':
    ''' Test this module here '''


