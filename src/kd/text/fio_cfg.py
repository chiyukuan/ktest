#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import random
from kd.util.logger import getLogger

logger = getLogger(__name__)

class FioCfg(object):

    # read/write/readwrite:70/randread/randwrite/randrw:70
    # runSpec: [txSize, read percentage, random percentage]
    def __init__(self, runTime, runSpec, osio=8, workerPerTarget=1, ioengine='libaio', bw=None, verify=None, doVerify=False):
        if runTime is None:
            self.runSec = None
        else:
            self.runSec = ( (runTime[0] * 60) + runTime[1] ) * 60 + runTime[2]
        self.osio   = osio
        self.ioengine = ioengine
        self.bw       = bw
        self.verify   = verify
        self.doVerify = doVerify
        self.txSz, self.readPer, self.randPer = runSpec
        if self.randPer != 0 and self.randPer != 100:
            logger.error("random percentage must be 0 or 100")
        else:
            if self.readPer == 100:
                self.aSpecName = 'randread' if self.randPer == 100 else 'read'
            elif self.readPer == 0:
                self.aSpecName = 'randwrite' if self.randPer == 100 else 'write'
            else:
                if self.randPer == 100:
                    self.aSpecName = 'randrw'
                else:
                    self.aSpecName = 'readwrite'

    def write(self, filename, targets):
        self.fd = open(filename, 'w')
        self.fd.write('[global]\n')
        if self.ioengine == 'libaio':
            self.fd.write('direct=1\n')
        self.fd.write('rw=%s\n' % self.aSpecName)
        self.fd.write('rwmixread=%d\n' % self.readPer)
        self.fd.write('ioengine=%s\n' % self.ioengine)
        if isinstance(self.txSz,int):
            self.fd.write('bs=%dk\n' % (self.txSz / 1024))
        else:
            if "-" in self.txSz:
                self.fd.write('bs=4k\n')
                self.fd.write('bsrange=%s,%s\n' % (self.txSz,self.txSz))
            else:
                # ":" in self.txSz:
                self.fd.write('bs=4k\n')
                self.fd.write('bssplit=%s,%s\n' % (self.txSz,self.txSz))
        if self.bw is not None:
            unit = self.bw[-1]
            rwBw = int( self.bw[:-1] ) / len(targets)
            rdBw = ( rwBw * self.readPer ) / 100
            wrBw = rwBw - rdBw
            self.fd.write('rate=%d%s,%d%s\n' % (rdBw, unit, wrBw, unit))

        self.fd.write('iodepth=%d\n' % self.osio)
        self.fd.write('numjobs=1\n')
        self.fd.write('group_reporting=1\n')
        self.fd.write('randseed=%d\n' % random.randrange(4096))
        if self.verify is not None:
            self.fd.write('verify=%s\n' % self.verify)
        self.fd.write('name=fio_%s\n' % (self.aSpecName))
        self.fd.write('\n')

        for idx in range(len(targets)):
            target = targets[idx]
            self.fd.write('[job_%03d]\n' % idx)
            self.fd.write('filename=%s\n' % target[0])
            self.fd.write('size=%dm\n' % (target[1] >> 20))

            if self.runSec is None or self.doVerify:
                self.fd.write('time_based=0\n')
            else:
                self.fd.write('time_based=1\n')
                self.fd.write('runtime=%d\n' % self.runSec)

            if self.doVerify:
                self.fd.write('create_serialize=0\n')
                self.fd.write('verify_fatal=1\n')
                self.fd.write('verify_dump=1\n')
                self.fd.write('do_verify=1\n')
            else:
                self.fd.write('do_verify=0\n')
            self.fd.write('\n')

        self.fd.close()

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    #fioCfg = FioCfg([0, 1, 30], ['4k-64k', 0, 100], osio=16)
    fioCfg = FioCfg([0, 1, 30], ['4k/10:64k/50:32k/40', 0, 100], osio=16)
    #fioCfg = FioCfg([0, 1, 30], [1024*1024, 0, 100], osio=16)
    fioCfg.write('test.fio', [('/dev/sda', 80 * 1024)])


