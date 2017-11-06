#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
import time
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.tfwk.test_case import TestCase
from kd.tcases.tc_bench import TcBench
from kd.text.kd_ctnr import KdCtnr

logger = getLogger(__name__)

class TchDockCtnr(TestCase):

    def __init__(self, ctnrSpec=None, ctnrUrl=None):
        if ctnrSpec is not None:
            desc = 'Dock CTNR %d, %d GB in %d vdisk' % (
                    ctnrSpec[0], sum(ctnrSpec[1]), len(ctnrSpec[1]))
        else:
            desc = 'Dock CTNR from %s' % ctnrUrl

        super(TchDockCtnr, self).__init__(None, desc)
        self.ctnrSpec    = ctnrSpec
        self.ctnrUrl     = ctnrUrl
        self.stageCtnrFN = '/tmp/ktest_stage_container.xml'

        # add steps
        if self.ctnrSpec is not None:
            self.addStep("generate dockContainer file",  self._genDockCtnrXml) ;
        else:
            self.addStep("Copy dockContainer file",      self._copyDockCtnrXml) ;
        self.addStep("Stage and Dock Container file",    self._stageDockCtnrXml) ;
        self.addStep("Check Container",                  self._checkCtnr) ;

    @classmethod
    def allTestCases(cls):
        ctnrSpecs = cls.getParamEval( 'ctnr.specs' )
        ctnrUrls  = cls.getParamEval( 'ctnr.urls' )

        tcases = []
        if bool(ctnrSpecs):
            for ctnrSpec in ctnrSpecs:
                tcases.append( cls('Stage and Dock the container',
                                   ctnrSpec, None) )
        if bool(ctnrUrls):
            for ctnrUrl in ctnrUrls:
                tcases.append( cls('Stage and Dock the container',
                                   None, Url.fromStr(ctnrUrl)) )
        return tcases

    def _prepare(self, step):
        self.bench = TcBench()

        self.bench.openKnsHosts(step)
        if not step.canContinue():
            return
        self.kns = self.bench.getKnsHost()

        self.bench.openLocalHost(step)
        if not step.canContinue():
            return
        self.local  = self.bench.getLocalHost()

    def _tearDown(self, step):
        self.bench.close(step)

    def _genDockCtnrXml(self, step):
        ahosts = []
        idx = 0
        for host in self.bench.getAppHosts():
            ahosts.append('apphost%02d' % idx) ;
            idx += 1

        ctnr = KdCtnr(self.ctnrSpec[0], 'Ctrn_%d' % self.ctnrSpec[0])
        if len(self.ctnrSpec) > 2:
            ctnr.addVDisks(self.ctnrSpec[1], hosts=ahosts, protPcy=self.ctnrSpec[2])
        else:
            ctnr.addVDisks(self.ctnrSpec[1], hosts=ahosts)

        ctnr.write(self.stageCtnrFN)
        return

    def _copyDockCtnrXml(self, step):
        execUrlSess( Url.fromUrl(self.dockCtnrUrl, protocol='scp'),
                     scpTo=self.stageCtnrFN )
        return

    def _stageDockCtnrXml(self, step):
        while True:
            self.local.run('/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                            '-d @%s %s/stage/data_container' % (self.stageCtnrFN, self.kns.getKnsUrl()))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break

            self.local.run('/bin/curl -L -X PUT -H "Content-Type: application/xml" '\
                            '%s/dock/data_container/%d' % (self.kns.getKnsUrl(), self.ctnrSpec[0]))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break

            step.setRC(RC.OK, 'Add following %d vdisks, %s' % (
                        len(self.ctnrSpec[1]), self.ctnrSpec[1]) )
            break

        return

    def _checkCtnr(self, step):
        waitTime  = 600
        sleepTime =  10
        cmd       = '/bin/curl -L %s/data_container/%d > %s_new' % (
                self.kns.getKnsUrl(), self.ctnrSpec[0], self.stageCtnrFN)

        while True:
            time.sleep( sleepTime )
            self.local.run(cmd)
            if os.path.getsize(self.stageCtnrFN) != 0:
                break

            waitTime -= sleepTime
            if waitTime < 0:
                step.setRC(RC.ERROR, "Could not access teh container %d from kns in %d sec" % (
                            self.ctnrSpec[0], waitTime))
                return
        return


if __name__ == '__main__':
    ''' Test this module here '''


