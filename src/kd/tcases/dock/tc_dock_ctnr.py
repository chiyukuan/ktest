#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
import time
from kd.util.logger import getLogger
from kd.tcases.tc_base       import TcBase
from kd.util.rc_msg import RC
from kd.util.kspawn import execUrlSess
from kd.text.kd_ctnr import KdCtnr

logger = getLogger(__name__)

class TcDockCtnr(TcBase):

    def __init__(self, ctnrSpec, aHostIdxList=[], sshTunnel=False):

        self.ctnrName    = ctnrSpec[0]
        self.curlCmds = [('/tmp/auto_container.xml', 'kns', 'post', 'stage/data_container'),
                          (None, 'kns', 'put',  'dock/data_container/' + self.ctnrName)]
        if len(ctnrSpec) == 1:
            desc = 'undock container %s' % self.ctnrName
            super(TcDockCtnr, self).__init__(desc)

            self.addStep("undock Container", self._undock) ;

        else:
            self.vdiskSzList = ctnrSpec[1]
            self.protPcy     = None if len(ctnrSpec) < 3 else ctnrSpec[2]
            self.aHostIdxList = aHostIdxList

            desc = 'Dock container %s, %d GB in %d vdisk%s' % (
                    self.ctnrName, sum(self.vdiskSzList),
                    len(self.vdiskSzList),
                    " no protection" if self.protPcy is None else " in %s" % self.protPcy)

            super(TcDockCtnr, self).__init__(desc)

            self.addStep("generate dockContainer file",  self._genDockCtnrXml) ;
            if sshTunnel:
                self.addStep_scpToDockHosts( self.curlCmds ) ;
                self.addStep_doCurlCmds("Stage and Dock Container file", self.curlCmds) ;
            else:
                self.addStep("Stage and Dock Container file",self._stageDockCtnrXml) ;

            if not sshTunnel:
                #  @todo enable it later
                self.addStep("Check Container",              self._checkCtnr) ;
            self.addStep("Backup Files",                     self._backup)


    @classmethod
    def allTestCases(cls):
        return []

    def _prepare(self, step):
        super(TcDockCtnr, self)._prepare(step, dockHost=True, localHost=True)

        self.kns = self.bench.getKnsHost()

    def _genDockCtnrXml(self, step):
        fname    = self.curlCmds[0][0]
        appHosts = self.bench.getAppHosts()
        ahosts = []
        idx = -1
        for hostIdx in range(len(appHosts)):
            idx += 1
            if bool(self.aHostIdxList) and hostIdx not in self.aHostIdxList:
                continue
            host = appHosts[hostIdx]
            ahosts.append('host%02d' % idx) ;

        ctnr = KdCtnr(self.ctnrName)
        if len(ahosts) <= 1:
            ctnr.addVDisks(self.vdiskSzList, hosts=ahosts, protPcy=self.protPcy)
        else:
            aHostCnt = len(ahosts)
            vdiskCnt = len(self.vdiskSzList)
            for aHostIdx in range(aHostCnt):
                vdiskList = [ self.vdiskSzList[ii] for ii in
                                    range(aHostIdx, vdiskCnt, aHostCnt) ]
                ctnr.addVDisks(vdiskList, hosts=[ahosts[aHostIdx]], protPcy=self.protPcy)

        ctnr.write( fname )
        return

    def _stageDockCtnrXml(self, step):
        while True:
            self.local.run('/bin/curl -L -X POST -H "Content-Type: application/xml" '\
                            '-d @%s %s/%s' % \
                            (self.curlCmds[0][0], self.kns.getKnsUrl(), self.curlCmds[0][3]))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break

            self.local.run('/bin/curl -L -X PUT -H "Content-Type: application/xml" '\
                            '%s/%s' % (self.kns.getKnsUrl(), self.curlCmds[1][3]))
            if self.local.getRC() != RC.OK:
                step.setRC(self.local.getRC(), (self.local.getRslt()))
                break

            step.setRC(RC.OK, 'Add following %d vdisks, %s' % (
                        len(self.vdiskSzList), self.vdiskSzList) )
            break

        return

    def _undock(self, step):
        self.local.run('/bin/curl -L -X PUT -H "Content-Type: application/xml" '\
                       '%s/data_container/%s?action=undock' % (self.kns.getKnsUrl(), self.ctnrName))
        if self.local.getRC() != RC.OK:
            step.setRC(self.local.getRC(), (self.local.getRslt()))

        time.sleep( 10 )
        self.local.run('/bin/curl -L -X DELETE -H "Content-Type: application/xml" '\
                       '%s/data_container/%s' % (self.kns.getKnsUrl(), self.ctnrName))
        if self.local.getRC() != RC.OK:
            step.setRC(self.local.getRC(), (self.local.getRslt()))

    def _backup(self, step):
        fname    = self.curlCmds[0][0]
        self.local.run('mv %s %s/%s' % (fname, TcBase.getWorkDir(), fname[4:]))

    def _checkCtnr(self, step):

        waitTime  = 600
        sleepTime =  10
        cmd       = '/bin/curl -L %s/data_container/%s > %s_new' % (
                self.kns.getKnsUrl(), self.ctnrName, self.curlCmds[0][0])

        while True:
            time.sleep( sleepTime )
            self.local.run(cmd)
            if os.path.getsize( self.curlCmds[0][0] ) != 0:
                break

            waitTime -= sleepTime
            if waitTime < 0:
                step.setRC(RC.ERROR, "Could not access teh container %s from kns in %d sec" % (
                            self.ctnrName, waitTime))
                return
        return


if __name__ == '__main__':
    ''' Test this module here '''



