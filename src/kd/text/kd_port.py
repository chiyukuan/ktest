#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom.minidom import Document
from kd.text.xml_base import XmlBase

class KdPort(XmlBase):

    def __init__(self):
        self.dockNames = {}
        self.docGen = False

    def addKns(self, dockName, knsAddr):
        if dockName in self.dockNames:
            knsAddrs = self.dockNames[dockName]
        else:
            knsAddrs = []
            self.dockNames[dockName] = knsAddrs

        knsAddrs.append( knsAddr )
        self.docGen = False


    def _genXml(self):
        if self.docGen:
            return
        # create new doc
        self.doc    = Document()
        self.root   = self.doc.createElement('dockport_resources')
        self.doc.appendChild( self.root )

        for dockName in self.dockNames:
            knsAddrs = self.dockNames[dockName]
            dElm = self.doc.createElement('dock')
            self.root.appendChild( dElm )
            pairs = [ ('dock_name', dockName) ]
            for knsAddr in knsAddrs:
                pairs.append( ('kns', knsAddr) )

            self._pairToXml( dElm, pairs )

        self.docGen = True

if __name__ == '__main__':
    ''' Test this module here '''
    kdPort = KdPort()
    kdPort.addKns('000102030405060708090A0B0C0D0E0F', '172.16.13.128:4001')
    kdPort.write('test.xml')


