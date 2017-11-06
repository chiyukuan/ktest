#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import json
from kd.util.logger import getLogger
from kd.text.kd_dcfg import KdDNode

logger = getLogger(__name__)

class KdKdcdDnlist(object):

    def __init__(self, jsonFN):
        with open(jsonFN) as dFile:
            self.data = json.load( dFile )
        if isinstance(self.data, dict):
            self.data = [ self.data ]

    def getDNodes(self):
        dNodes = []

        for node in self.data:
            services = []
            for svcName in ('dock_reflector', 'kns', 'poolkeeper', 'tilekeeper'):
                if node['services'][svcName]['isActive'] != \
                        node['services'][svcName]['isEnabled']:
                    services.append( None )
                else:
                    services.append( node['services'][svcName]['isEnabled'] )

            dn = KdDNode( node['id'], None,
                          node['mgmtIP'],
                          node['port'] - 4,
                          services=services,
                          plateId=node['dockPlateID'],
                          rackId=node['virtualRackID'] )

            dNodes.append( dn )
        return dNodes


    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

    dnList = KdKdcdDnlist('/tmp/ktest_registry_tkcd_dnlist.json')
    dns = dnList.getDNodes()
    dns2 = dnList.getDNodes()

    if dns[0] == dns[0]:
        print "OK"

    dns2[0].svcTK = False
    if dns[0] == dns2[0]:
        print "Error"
