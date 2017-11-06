#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom.minidom import Document
from kd.text.xml_base import XmlBase

class KdResXml(XmlBase):

    def __init__(self):
        self.disks   = []
        self.mgmtIfs = []
        self.dataIfs = []

        self.docGen = False

    def addDisk(self, devName, name=None, devType='Fast'):
        if name is None:
            name = "%s%02d" % (devType, len(self.disks))

        self.disks.append( [name, devType, devName] )
        self.docGen = False

    def addMgmtIf(self, name):
        self.mgmtIfs.append( name )
        self.docGen = False

    def addDataIf(self, name):
        self.dataIfs.append( name )
        self.docGen = False

    def getDataIfCnt(self):
        return len(self.dataIfs)

    def _genXml(self):
        if self.docGen:
            return
        # create new doc
        self.doc    = Document()
        self.root   = self.doc.createElement('dockhost_resources')
        self.doc.appendChild( self.root )

        # cpu
        self.cpu = self.doc.createElement('cpu')
        self.root.appendChild( self.cpu )

        # mem
        self.mem = self.doc.createElement('memory')
        self.root.appendChild( self.mem )

        #disk
        for disk in self.disks:
            dElm = self.doc.createElement('disk')
            self._pairToXml( dElm, [ ('name',   disk[0]),
                                     ('type',   disk[1]),
                                     ('drive',  disk[2]) ] )
            self.root.appendChild( dElm )

        #mgmt if
        for mgmtIf in self.mgmtIfs:
            elm = self.doc.createElement('mgmt_interface')
            elm.appendChild( self.doc.createTextNode(mgmtIf) )
            self.root.appendChild( elm )

        #data if
        for dataIf in self.dataIfs:
            elm = self.doc.createElement('data_interface')
            elm.appendChild( self.doc.createTextNode(dataIf) )
            self.root.appendChild( elm )

        self.docGen = True

if __name__ == '__main__':
    ''' Test this module here '''
    resXml = KdResXml()
    #resXml.addDisk('/dev/kodiak/fast-vol-sdb')
    #resXml.addDisk('/dev/kodiak/fast-vol-sdc')
    resXml.addMgmtIf('eth0')
    resXml.addDataIf('eth0')
    resXml.write('test.xml')

