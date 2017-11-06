#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom.minidom import Document
from kd.text.xml_base import XmlBase

class KdProtPcy( XmlBase ):
    def __init__(self, pcyName):
        self.pcyName = pcyName
        self.svr_erasure_coding   = False
        self.svr_replication      = False
        self.rack_erasure_coding  = False
        self.rack_replication     = False
        if self.pcyName == '4+1_32k' or self.pcyName == 'P_4x1_32k':
            self.svr_erasure_coding   = True
            self.svr_erasure_data     = 4
            self.svr_erasure_erasure  = 1
            self.svr_erasure_stripe   = 32
        if self.pcyName == '8+1_8k' or self.pcyName == 'P_8x1_8k':
            self.svr_erasure_coding   = True
            self.svr_erasure_data     = 8
            self.svr_erasure_erasure  = 1
            self.svr_erasure_stripe   = 8

        if self.pcyName == '__1+1' or self.pcyName == 'P__1x1':
            self.rack_replication     = True
            self.rack_replication_factor = 2
        if self.pcyName == '__1+2' or self.pcyName == 'P__1x2':
            self.rack_replication     = True
            self.rack_replication_factor = 3

        if self.pcyName == '4+1_32k__1+1' or self.pcyName == 'P_4x1_32k__1x1':
            self.svr_erasure_coding   = True
            self.svr_erasure_data     = 4
            self.svr_erasure_erasure  = 1
            self.svr_erasure_stripe   = 32
            self.rack_replication     = True
            self.rack_replication_factor = 2
        if self.pcyName == '8+1_8k__1+1' or self.pcyName == 'P_8x1_8k__1x1':
            self.svr_erasure_coding   = True
            self.svr_erasure_data     = 8
            self.svr_erasure_erasure  = 1
            self.svr_erasure_stripe   = 8
            self.rack_replication     = True
            self.rack_replication_factor = 2

        if self.pcyName == '4+1_32k__1+2' or self.pcyName == 'P_4x1_32k__1x2':
            self.svr_erasure_coding   = True
            self.svr_erasure_data     = 4
            self.svr_erasure_erasure  = 1
            self.svr_erasure_stripe   = 32
            self.rack_replication     = True
            self.rack_replication_factor = 3
        if self.pcyName == '8+1_8k__1+2' or self.pcyName == 'P_8x1_8k__1x2':
            self.svr_erasure_coding   = True
            self.svr_erasure_data     = 8
            self.svr_erasure_erasure  = 1
            self.svr_erasure_stripe   = 8
            self.rack_replication     = True
            self.rack_replication_factor = 3

    def _genXml(self, doc=None, pElm=None):
        self.doc = doc
        
        elm = self.doc.createElement('data_protection_policy')
        pElm.appendChild( elm )

        nElm = self.doc.createElement('name')
        nElm.appendChild( self.doc.createTextNode( self.pcyName ) )
        elm.appendChild( nElm )

        if self.svr_erasure_coding or self.svr_replication or \
           self.rack_erasure_coding or self.rack_replication:
            svrElm = self.doc.createElement('server')
            elm.appendChild( svrElm )

            if self.svr_erasure_coding:
                eraElm = self.doc.createElement('erasure_coding')
                svrElm.appendChild( eraElm )

                self._pairToXml( eraElm,
                        [ ('data',    self.svr_erasure_data),
                          ('erasure', self.svr_erasure_erasure),
                          ('stripe',  self.svr_erasure_stripe),
                        ] )
            elif self.svr_replication:
                repElm = self.doc.createElement('replication')
                svrElm.appendChild( repElm )

                self._pairToXml( repElm,
                        [ ('factor', self.svr_replication_factor) ] )

            rackElm = self.doc.createElement('rack')
            elm.appendChild( rackElm )

            if self.rack_erasure_coding:
                eraElm = self.doc.createElement('erasure_coding')
                rackElm.appendChild( eraElm )

                self._pairToXml( eraElm,
                        [ ('data',    self.rack_erasure_data),
                          ('erasure', self.rack_erasure_erasure),
                          ('stripe',  self.rack_erasure_stripe),
                        ] )
            elif self.rack_replication:
                repElm = self.doc.createElement('replication')
                rackElm.appendChild( repElm )

                self._pairToXml( repElm,
                        [ ('factor', self.rack_replication_factor) ] )



class KdVDisk( XmlBase ):

    def __init__(self, size, name=None, vrtlRackId=None,
                            dType=None, bSize=None, dState=None):
        self.size       = size
        self.name       = name
        self.dState     = dState
        self.vrtlRackId = vrtlRackId
        self.dType      = 'Fast' if dType is None else dType
        self.bSize      = None if bSize == 4096 else bSize

    def _genXml(self, doc=None, pElm=None):
        self.doc = doc

        vdElm = self.doc.createElement('vdisk')
        pElm.appendChild( vdElm )

        self._pairToXml( vdElm,
                [ ('id',              None),
                  ('state',           self.dState),
                  ('block_size',      self.bSize),
                  ('type',            self.dType),
                  ('name',            self.name),
                  ('size',            self.size),
                  ('virtual_rack_id', self.vrtlRackId),
                ] )

class KdVDiskSet( XmlBase ):

    def __init__(self, name, vrtlRackId=None, bSize=None, hosts=[], protPcy=None ):
        self.name       = name
        self.vrtlRackId = vrtlRackId
        self.bSize      = None if bSize == 4096 else bSize
        self.hosts      = hosts
        self.protPcy    = protPcy
        self.vdisks     = []


    def addVDisk(self, vdisk):
        self.vdisks.append( vdisk )

    def addHost(self, host):
        self.hosts.append(host)

    def _genXml(self, doc=None, pElm=None):
        self.doc = doc
        vsElm = doc.createElement('vdisk_set')
        pElm.appendChild( vsElm )
            
        pairs = [('name',            self.name),
                 ('id',              None),
                 ('virtual_rack_id', self.vrtlRackId),
                 ('block_size',      self.bSize),
                 ('data_protection', self.protPcy),
                ]

        if self.hosts is not None:
            for host in self.hosts:
                pairs.append( ('attach', host) )

        self._pairToXml( vsElm, pairs )

        for vdisk in self.vdisks:
            vdisk._genXml( self.doc, vsElm )

class KdCtnr( XmlBase ):

    def __init__(self, name, dockPlateId=None, vrtlRackId=None, aHosts=[],
                                     protPcy=None):
        self.vdiskCnt    = 0
        self.name        = name
        self.dockPlateId = dockPlateId
        self.vrtlRackId  = vrtlRackId
        self.aHosts      = aHosts
        self.vdiskSets   = []
        self.pcyNames    = ['4+1_32k', '8+1_8k', '__1+2']
        self.pcyNames    = []

    def _genXml(self, doc=None, pElm=None):
        # create new doc
        if doc is not None and pElm is not None:
            self.doc  = doc
            self.root = pElm
        else:
            self.doc    = Document()
            self.root   = self.doc.createElement('data_container')
            self.doc.appendChild( self.root )

        self._pairToXml( self.root,
                         [('id',                    None),
                          ('dock_plate_id',         self.dockPlateId),
                          ('virtual_rack_id',       self.vrtlRackId),
                          ('name',                  self.name),
                          ('state',                 None),
                          ('created_on',            None),
                          ('last_modified_by',      'Ray Kuan'),
                          ('last_modified',         None),
                         ])

        for pcyName in self.pcyNames:
            pcy = KdProtPcy( pcyName )
            pcy._genXml( self.doc, self.root )

        self.root.appendChild( self.doc.createElement('data_protection') )

        for aHost in self.aHosts:
            elm = self.doc.createElement('host_access')
            elm.appendChild( self.doc.createTextNode(aHost) )
            self.root.appendChild( elm )

        for vdiskSet in self.vdiskSets:
            vdiskSet._genXml( self.doc, self.root )

    def addVDisk(self, name, size, bSize=4096,
                       vrtlRackId=None, dType='Fast', hosts=None):

        vdiskSet = KdVDiskSet( 'vDiskSet_%s' % name, vrtlRackId, bSize, hosts )
        vdiskSet.addVDisk( KdVDisk( size, name, vrtlRackId=vrtlRackId,
                            dType=dType, bSize=bSize ) )
        self.vdiskSets.append( vdiskSet )

    def addVDisks(self, szList, hosts=None, protPcy=None):

        if protPcy is not None and protPcy not in self.pcyNames:
            self.pcyNames.append( protPcy )

        vdiskSet = KdVDiskSet( 'vDiskSet_%d' % len( self.vdiskSets ), hosts=hosts, protPcy=protPcy )

        for szIdx in range(len(szList)):
            vdisk = KdVDisk( szList[szIdx],
                             'idx_%03d_%dG' % (szIdx, szList[szIdx]) )
            vdiskSet.addVDisk( vdisk )

        self.vdiskSets.append( vdiskSet )

if __name__ == '__main__':
    ''' Test this module here '''
    ctnr = KdCtnr(1, 'testCtnr')
    ctnr.addVDisks([10, 15, 20], hosts=['server1'],protPcy='__1+2')
    ctnr.addVDisks([10, 15, 20], hosts=['server2'])
    ctnr.write('test.xml')
    print ctnr


