#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import re
from kd.util.logger import getLogger

logger = getLogger(__name__)

class FioRslt(object):

    def __init__(self, fioRsltFN):
        self.name     = 'fio'
        self.iops     = 0
        self.bw       = 0.0
        self.respTime = 0.0
        self.errCnt   = 0
        self.error    = None
        with open(fioRsltFN, 'rb') as f:
            lines = f.read().splitlines()

            for line in lines:
                if "error" in line:
                    token = re.search('err=[^\)]*\)', line).group(0)
                    tokens = token.split('(')
                    self.error = token[4:]
                    self.errCnt = int( tokens[0][4:] )
                if line.startswith('  write:'):
                    words = line.split()
                    if words[2].endswith('MB/s,'):
                        self.bw   += float( words[2][3:-5] )
                    if words[2].endswith('KB/s,'):
                        self.bw   += float( words[2][3:-5] ) / 1024.0
                    else:
                        self.bw   += float( words[2][3:-5] ) / (1024.0 * 1024.0)
                    if words[3].endswith('K,'):
                        self.iops += int( float(words[3][5:-2]) * 1024 )
                    else:
                        self.iops += int(words[3][5:-1])

                elif line.startswith('  read :'):
                    words = line.split()
                    if words[3].endswith('MB/s,'):
                        self.bw   += float( words[3][3:-5] )
                    else:
                        self.bw   += float( words[3][3:-5] ) / 1024.0
                    if words[4].endswith('K,'):
                        self.iops += int( float(words[4][5:-2]) * 1024 )
                    else:
                        self.iops += int(words[4][5:-1])

                elif line.startswith('     lat (usec):'):
                    words = line.split()
                    self.respTime += float(words[4][4:-1]) / 1000

                elif line.startswith('     lat (msec):'):
                    words = line.split('=')
                    w2 = words[3].split()
                    self.respTime += float(w2[0][:-1])

    def getAccessSpec(self):
        return self.name

    def getIOps(self):
        return self.iops

    def getBW(self):
        return self.bw

    def getRespTime(self):
        return self.respTime

    def __str__(self):
        if self.errCnt == 0:
            return "Spec:%s %d IO/sec %.2f MB/sec %.2f ms" % (
                    self.getAccessSpec(), self.getIOps(),
                     self.getBW(), self.getRespTime())
        else:
            print self.error
            return "Spec:%s %d IO/sec %.2f MB/sec %.2f ms %d err" % (
                    self.getAccessSpec(), self.getIOps(),
                     self.getBW(), self.getRespTime(), self.errCnt)

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

    rslt = FioRslt('my.rslt')

    print rslt
