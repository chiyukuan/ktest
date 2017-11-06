#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.text.xml_base import XmlBase

class KdApiKns(XmlBase):

    def __init__(self, apiKnsFN):
        super(KdApiKns, self).__init__( inXmlFN=apiKnsFN )

    @staticmethod
    def urlPath():
        return "/kodiak/api/kns"

    def getPrimaryKns(self):
        ret = None
        knsList = self.doc.getElementsByTagName('kns')
        for kns in knsList:
            isPri = kns.getElementsByTagName('is_primary')
            if isPri[0].childNodes[0].nodeValue == 'true':
                dockNodeId = kns.getElementsByTagName('docknode_id')
                dockHostId = kns.getElementsByTagName('dockhost_id')
                isSync     = kns.getElementsByTagName('is_sync')
                ipAddr     = kns.getElementsByTagName('ip_address')
                port       = kns.getElementsByTagName('port')

                ret = [ int(dockNodeId[0].childNodes[0].nodeValue),
                        int(dockHostId[0].childNodes[0].nodeValue),
                        bool(isSync[0].childNodes[0].nodeValue),
                        ipAddr[0].childNodes[0].nodeValue.encode('ascii','ignore'),
                        int(port[0].childNodes[0].nodeValue),
                        True ]
        return ret

if __name__ == '__main__':
    ''' Test this module here '''
    kdApiKns = KdApiKns('/tmp/kns.xml')
    print kdApiKns.getPrimaryKns()

