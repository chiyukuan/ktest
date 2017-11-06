#! /usr/bin/env python


from kd.util.logger import getLogger
from kd.tcases.tc_base import TcBase

logger = getLogger(__name__)

class TcIo(TcBase):

    def __init__(self, cmd, txSz=8192):
        super(TcIo, self).__init__('%s at tile level' % cmd)
        # border-write
        # verify
        self.cmd    = cmd
        self.ptnIdx = 1
        self.txSz   = txSz
        self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )

        if ( cmd.lower().endswith('write') ):
            self.addStep('write at tile level',  self._write)
        if ( cmd.lower().endswith('verify') ):
            self.addStep('verify at tile level', self._verify)

    def _prepare(self, step):
        super(TcIo, self)._prepare(step, appHost=True, localHost=True)


    def _write(self, step):
        for host in self.bench.getAppHosts():
          for dev in host.devs:
            # open device for write
            for tileAddr in range(0, dev.sz, 1 << 30):
              for addr in [tileAddr, tileAddr + (1 << 30) - self.txSz]:
                host.run('/bin/dd if=/root/dd_pattern/%02x.bin of=%s '\
                         'bs=%d seek=%d count=1 oflag=direct,seek_bytes' % (
                         self.ptnIdx, dev.name, self.txSz, addr))
                self.ptnIdx += 1
            # close device

    def _verify(self, step):
        for host in self.bench.getAppHosts():
          for dev in host.devs:
            # open device for read
            fd = open(dev.name, "rb")
            print "\ndevice %s" % dev.name
            try:
              for tileAddr in range(0, dev.sz, 1 << 30):
                for addr in [tileAddr, tileAddr + (1 << 30) - self.txSz]:
                  fd.seek(addr, 0)
                  byte = fd.read(self.txSz)
                  print "0x%08x %s" % (addr, byte[0:16].encode('hex'))
            finally:
                # close device
                fd.close()

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


