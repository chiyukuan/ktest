#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom import minidom
from xml.dom.minidom import Document
from kd.text.xml_base import XmlBase


class KdPkList(XmlBase):

    def __init__(self, pkListFN):
        self.doc = minidom.parse(pkListFN)

    def getPrimaryPk(self):
        ret = None
        pkList = self.doc.getElementsByTagName('poolkeeper')
        for pk in pkList:
            isPri = pk.getElementsByTagName('isPrimary')
            if isPri[0].childNodes[0].nodeValue == 'true':
                ipAddr     = pk.getElementsByTagName('ip')
                port       = pk.getElementsByTagName('port')
                dockNodeId = pk.getElementsByTagName('dockNodeID')
                ret = [ int(dockNodeId[0].childNodes[0].nodeValue),
                        ipAddr[0].childNodes[0].nodeValue.encode('ascii','ignore'),
                        int(port[0].childNodes[0].nodeValue),
                        True ]

        return ret

if __name__ == '__main__':
    ''' Test this module here '''
    pkList = KdPkList('/tmp/aa')
    print pkList.getPrimaryPk()

