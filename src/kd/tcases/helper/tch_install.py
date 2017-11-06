#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import time
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.tcases.tc_base import TcBase

logger = getLogger(__name__)

class TchInstall(TcBase):

    def __init__(self, desc, rpmUrl=None):
        super(TchInstall, self).__init__(None, desc)

        self.rpmCurr = '/tmp/auto_KodiakDataEngine_latest.rpm'

        self.rpmUrl = None if rpmUrl is None else Url.fromStr(rpmUrl)

        # add steps
        self.addStep("Copy rpm file",         self._cpRpm   ) ;
        self.addStep("uninstall kodiak apps", self._unintall) ;
        self.addStep("install Kodiak apps",   self._instiall) ;

    @classmethod
    def allTestCases(cls):
        return []

    def _prepare(self, step):
        if self.rpmUrl is None:
            self.rpmUrl = TchInstall.getParamUrl('rpm.url')

        super(TchInstall, self)._prepare(step, appHost=True, dockHost=True)
        if not step.canContinue():
            return

    def _tearDown(self, step):
        self.bench.close(step)

    def _cpRpm(self, step):
        execUrlSess( Url.fromUrl(self.rpmUrl, protocol='scp'),
                     scpTo=self.rpmCurr )

        for host in self.bench.getDockHosts():
            url = Url.fromUrl(host.url, protocol='scp', filename=self.rpmCurr)
            execUrlSess( url, scpFrom=self.rpmCurr )

        for host in self.bench.getAppHosts():
            url = Url.fromUrl(host.url, protocol='scp', filename=self.rpmCurr)
            execUrlSess( url, scpFrom=self.rpmCurr )


    def _unintall(self, step):

        for host in self.bench.getDockHosts():
            host.run('rpm -q KodiakContainer')
            if (host.getRC() == RC.OK):
                host.run('rpm -e %s' % host.getRslt())
            host.run('rpm -q KodiakDataEngine')
            if (host.getRC() == RC.OK):
                host.run('rpm -e %s' % host.getRslt())

        for host in self.bench.getAppHosts():
            host.run('rpm -q KodiakContainer')
            if (host.getRC() == RC.OK):
                host.run('rpm -e %s' % host.getRslt())
            host.run('rpm -q KodiakDataEngine')
            if (host.getRC() == RC.OK):
                host.run('rpm -e %s' % host.getRslt())


    def _instiall(self, step):

        for host in self.bench.getDockHosts():
            host.run('rpm -i %s' % self.rpmCurr)
            host.run('echo $?')
            if host.getRC() != RC.OK:
                step.rcMsg = host.getRcMsg()

        for host in self.bench.getAppHosts():
            host.run('rpm -q KodiakDataEngine')
            if (host.getRC() == RC.OK):
                continue
            host.run('yum install -y %s' % self.rpmCurr)
            host.run('echo $?')
            if host.getRC() != RC.OK:
                step.rcMsg = host.getRcMsg()

if __name__ == '__main__':
    ''' Test this module here '''


