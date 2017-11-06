#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import csv
from kd.util.logger import getLogger

logger = getLogger(__name__)

class IometerCsv(object):

    def __init__(self, csvFN):
        self.summaryRow = None
        with open(csvFN, 'rb') as csvFile:
            reader = csv.reader(csvFile)

            for row in reader:
                if row[0] != 'ALL':
                    continue
                self.summaryRow = row

    def getAccessSpec(self):
        return self.summaryRow[2]

    def getIOps(self):
        return int(float(self.summaryRow[6]))

    def getBW(self):
        return float(self.summaryRow[9])

    def getRespTime(self):
        return float(self.summaryRow[17])

    def __str__(self):
        return "Spec:%s %d IO/sec %.2f MB/sec %.2f ms" % (
                self.getAccessSpec(), self.getIOps(),
                 self.getBW(), self.getRespTime())

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    csv = IometerCsv('/home/rkuan/tmp/csv/ktest_iometer_16384_0_100.csv')
    print csv


