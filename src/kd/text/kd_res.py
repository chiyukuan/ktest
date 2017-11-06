#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import json
from kd.util.logger import getLogger

logger = getLogger(__name__)

class KdRes(object):

    def __init__(self, jsonFN):

        with open(jsonFN) as dFile:
            self.data = json.load( dFile )

    def getDisk(self):
        return self.data['resources']['disk']

    def getMgmtIF(self):
        return self.data['resources']['mgmt_interface']

    def getDataIF(self):
        return self.data['resources']['data_interface']

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

    res = KdRes('/kodiak/dockhost/resources.cfg')

    print res.getDisk()
    for item in res.getDisk():
        print item['uuid']


