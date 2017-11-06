#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tcases.tc_base  import TcBase
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.text.kd_res_tile import KdResTile

logger = getLogger(__name__)

class TcIoTile(TcBase):
    classDesc = 'Access(bind) all tiles for all disk.'
    claaSDescDetail = \
'''
It accesses all nomad disks from begin of tile, end of tile, in the tile and between tiles to make sure
  - bind behavior in correct (need 4 unbinded disks),
  - and the all tile are bound after this test case.
'''

    def __init__(self, totalTileCnt=None, sshTunnel=False):
        super(TcIoTile, self).__init__('Bind all tiles for all vdisks')

        self.resTileFN      = '%s/ktest_res_tiles.xml' % TcBase.getWorkDir()
        self.devHostPairs   = []
        self.devHostPairIdx = 0
        self.wCnt = 0
        self.txSz = 8192
        self.totalSz = 0
        self.totalTileCnt = totalTileCnt

        self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
        self.addStep('perpare vdisk info',                self._vdiskPrepare)
        self.addStep('8k write at begin of tile on disk0',self._wrTile, opq=0)
        self.addStep('8k write at end of tile on disk1',  self._wrTile, opq=1)
        #self.addStep('8k write in tile at on disk2',      self._wrTile, opq=2)
        #self.addStep('8k write between tiles on disk3',   self._wrTile, opq=3)
        #self.addStep('8k write on other disk',            self._wrTile, opq=4)
        if not sshTunnel:
            self.addStep('Check the bound tile size/count',   self._check)

    @classmethod
    def allTestCases(cls):
        tcases = []
        tcases.append( cls() )
        return tcases

    def _prepare(self, step):
        super(TcIoTile, self)._prepare(step, appHost=True, localHost=True)

    def _vdiskPrepare(self, step):
        for host in self.bench.getAppHosts():
            for dev in host.devs:
                self.devHostPairs.append( (dev, host) )
                self.totalSz += dev.sz

    def _wrTile(self, step):
        print step
        self.devHostPairIdx = 0
        while True:
            if self.devHostPairIdx >= len(self.devHostPairs):
                break

            dev, host = self.devHostPairs[ self.devHostPairIdx ]
            self.devHostPairIdx += 1

            if step.opq == 0:
                addr = 0
            elif step.opq == 1:
                addr = (1024*1024*1024) - self.txSz
            elif step.opq == 2 or step.opq == 4:
                #addr = ((1024*1024*1024 - self.txSz) / 2 )
                addr = ((1024*1024*1024/2) - self.txSz )
            else:
                addr = 0

            while addr + self.txSz <= dev.sz:
                host.run('/bin/dd if=/root/dd_pattern/%02x.bin of=%s '\
                         'bs=%d seek=%d count=1 oflag=direct,seek_bytes' % (
                         self.wCnt, dev.name, self.txSz, addr))
                self.wCnt += 1
                if self.wCnt > 255:
                    self.wCnt = 0
                step.setRcMsg( host.getRcMsg() )
                if not step.canContinue():  break

                if step.opq == 3 and addr == 0:
                    addr = (1024*1024*1024) - (self.txSz/2)
                else:
                    addr += 1024 * 1024 * 1024

            #if step.opq != 4:
            #    break

    def _check(self, step):
        self.local.run('/bin/curl %s/utilization/tiles > %s' %
                       (self.bench.getKnsHost().getKnsUrl(), self.resTileFN))

        resTile = KdResTile(self.resTileFN)
        allocSz = resTile.getAllocTileSize()
        if allocSz != self.totalSz:
            step.setRC( RC.ERROR, 'total disk size, %d, is not same as allocated size, %d' % (self.totalSz, allocSz))

        if self.totalTileCnt is not None and self.totalTileCnt != resTile.getAllocTiles():
            step.setRC( RC.ERROR, 'Bind %d tiles but expected %d tiles' % (
                resTile.getAllocTiles(), self.totalTileCnt) )
        else:
            step.setRC( RC.OK, 'Bind %d tiles in total' % resTile.getAllocTiles() )

if __name__ == '__main__':
    ''' Test this module here '''



