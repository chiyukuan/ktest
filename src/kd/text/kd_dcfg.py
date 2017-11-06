#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom.minidom import Document
from kd.util.logger import getLogger
from kd.text.xml_base import XmlBase

logger = getLogger(__name__)

_NOTFOUND = object()

class KdDNodeTemplate(XmlBase):

    def __init__(self, name, basePort, plateId=None,
            services=[None, None, None], devices=[]):
        self.name     = name
        self.basePort = basePort
        self.plateId  = plateId
        self.svcKNS, self.svcPK, self.svcRefector = services
        self.devices  = devices

    def _genXml(self, doc=None, pElm=None):
        # create new doc
        if doc is not None and pElm is not None:
            self.doc  = doc
            self.root = pElm
        else:
            self.doc    = Document()
            self.root   = self.doc.createElement('dock')
            self.doc.appendChild( self.root )

        dElm = self.doc.createElement('docknode_template')
        self.root.appendChild( dElm ) ;

        pairs = [ ('template_name', self.name),
                  ('dock_plate_id', self.plateId),
                  ('base_port',     self.basePort),
                  ('service',       None),
                  ('memory',        None),
                  ('cpu',           None),
                ]
        for device in self.devices:
            pairs.append( ('device', device) )

        self._pairToXml( dElm, pairs )
        if bool(self.svcKNS) or bool(self.svcPK) or bool(self.svcRefector):
            self._pairToXml( dElm.getElementsByTagName('service')[0],
                             [ ('kns',            self.svcKNS),
                               ('poolkeeper',     self.svcPK),
                               ('dock_reflector', self.svcRefector),
                             ])

class KdDHost(XmlBase):
    class Node(object):
        def __init__(self, name, tmlName, port=None):
            self.name = name
            self.tmlName = tmlName
            self.port = port

        def getPairs(self):
            pairs = [ ('name',          self.name),
                      ('template_name', self.tmlName) ]

            if self.port is not None:
                pairs.append( ('base_port', self.port) )
            return pairs

    def __init__(self, name, rackId=None, hType=None):
        self.name      = name
        self.rackId    = rackId
        self.docknodes = []
        self.hType     = hType

    def addDNode(self, tmlName, name=None, port=None):
        if name is None:
            name = "%s_node%02d" % (self.name, len(self.docknodes))
        self.docknodes.append( KdDHost.Node(name, tmlName, port) )

    def _genXml(self, doc=None, pElm=None):
        # create new doc
        if doc is not None and pElm is not None:
            self.doc  = doc
            self.root = pElm
        else:
            self.doc    = Document()
            self.root   = self.doc.createElement('dock')
            self.doc.appendChild( self.root )

        hElm = self.doc.createElement('dockhost')
        self.root.appendChild( hElm ) ;

        self._pairToXml( hElm,
                         [ ('name',            self.name),
                           ('type',            self.hType),
                           ('virtual_rack_id', self.rackId),
                         ])

        for docknode in self.docknodes:
            nElm = self.doc.createElement('docknode')
            self._pairToXml( nElm, docknode.getPairs() )
            hElm.appendChild( nElm )


class KdDNode(object):

    def __init__(self, nId, macAddr, ipAddr, basePort,
                       services=[False, False, False, True],
                       plateId=1, rackId=1, name=None):
        self.nId      = nId
        self.name     = 'dockNode_%d' % nId if name is None else name
        self.macAddr  = macAddr
        self.ipAddr   = ipAddr
        self.basePort = basePort
        self.ssds     = []
        self.ifs      = []
        self.svcRefector, self.svcKNS, self.svcPK, self.svcTK = services
        self.plateId  = plateId
        self.rackId   = rackId

    def addDevice(self, deviceName, deviceType='ssd'):
        self.ssds.append( deviceName )

    def addInterface(self, name, addr):
        self.ifs.append( (name, addr) )

    def getServices(self):
        services = []
        if self.svcRefector:
            services.append('dock_reflector')
        if self.svcKNS:
            services.append('kns')
        if self.svcPK:
            services.append('poolkeeper')

        return services

    def setServices(self, services):
        self.svcRefector = True if 'all' in services or 'dock_reflector' in services else False
        self.svcKNS      = True if 'all' in services or 'kns' in services else False
        self.svcPK       = True if 'all' in services or 'poolkeeper' in services else False

    def __eq__(self, other):
        for attr in ['nId', 'ipAddr', 'basePort',
                     'svcRefector', 'svcKNS', 'svcPK', 'svcTK',
                     'plateId', 'rackId']:
            v1, v2 = [getattr(obj, attr, _NOTFOUND) for obj in [self, other]]
            if v1 is _NOTFOUND or v2 is _NOTFOUND:
                logger.error("Attr %s not found" % attr)
                return False
            elif v1 != v2:
                logger.error("Attr %s is not equal" % attr)
                return False
        return True

    def __ne__(self, other):
        return not self == other

class KdDcfg(XmlBase):

    def __init__(self, uuid, name, clusterMode='unicast', clusterMAddr=None):
        self.uuid = uuid
        self.name = name
        self.keep_alive_interval = None
        self.keep_alive_multiplier = None
        self.authentication_type = None
        self.authentication_key = None
        self.clusterMode = clusterMode
        self.clusterMAddr = clusterMAddr
        self.dockNodeTmls = []
        self.dockHosts = []
        self.cfgRes   = False
        self.cfgResTK = None
        self.placementLocality = None
        self.placementOverflow = None


    def tileKeeperRes(self, res):
        self.cfgRes   = True
        self.cfgResTK = res

    def setPlacement(self, locality=None, overflow=None):
        self.placementLocality = locality
        self.placementOverflow = overflow

    def _genXml(self, doc=None, pElm=None):
        # create new doc
        if doc is not None and pElm is not None:
            self.doc  = doc
            self.root = pElm
        else:
            self.doc    = Document()
            self.root   = self.doc.createElement('dock')
            self.doc.appendChild( self.root )

        self._pairToXml( self.root,
                         [ ('dock_uuid',        self.uuid),
                           ('name',             self.name),
                           ('last_modified',    None),
                           ('last_modified_by', None),
                           ('version',          None),
                           ('contact',          None),
                           ('dock_cluster',     None),
                           ('resource',         None),
                           ('data_placement',   None),
                         ])

        self._pairToXml( self.root.getElementsByTagName('contact')[0],
                         [ ('name',      'RayKuan'),
                           ('phone',     '888-123-4567'),
                           ('email',     'ray@kodiakdata.com'),
                         ])

        cElm = self.root.getElementsByTagName('dock_cluster')[0]
        self._pairToXml( cElm,
                         [ ('keep_alive_interval',  self.keep_alive_interval),
                           ('keep_alive_multiplier',self.keep_alive_multiplier),
                           ('authentication_type',  self.authentication_type),
                           ('authentication_key',   self.authentication_key),
                           ('dock_discovery',       None),
                         ])


        self._pairToXml( cElm.getElementsByTagName('dock_discovery')[0],
                         [ ('mode',      self.clusterMode),
                           ('mcast_addr',self.clusterMAddr),
                         ])

        if self.cfgRes:
            if self.cfgResTK is not None:
                for ii in range( 5 - len(self.cfgResTK) ):
                    self.cfgResTK.append( None )

                tElm = self.doc.createElement('tilekeeper')
                self._pairToXml( tElm,
                                 [ ('memory',           self.cfgResTK[0]),
                                   ('segment_size',     self.cfgResTK[1]),
                                   ('cpu_count',        self.cfgResTK[2]),
                                   ('cpu_set',          self.cfgResTK[3]),
                                   ('data_connections', self.cfgResTK[4]),
                                 ]
                               )
                self.root.getElementsByTagName('resource')[0].appendChild( tElm )

        self._pairToXml( self.root.getElementsByTagName('data_placement')[0],
                         [ ('locality',  self.placementLocality),
                           ('overflow',  self.placementOverflow),
                         ])

        for dockNodeTmp in self.dockNodeTmls:
            dockNodeTmp._genXml(self.doc, self.root)

        for dockHost in self.dockHosts:
            dockHost._genXml(self.doc, self.root)

    def addDNodeTml(self, dockNodeTml):
        self.dockNodeTmls.append( dockNodeTml )

    def addDHost(self, dockHost):
        self.dockHosts.append( dockHost )

    def addHost(self, mac, ip, res, nodesParam):
        nodes = []
        for basePort, svcNames in nodesParam:
            node = KdDNode( self.nId, mac, ip, basePort)
            if svcNames is not None:
                node.setServices( svcNames )
            nodes.append( node )
            self.nId += 1

        nodeLen = len(nodes)

        ssds = res.getSsds()
        for idx in range(len(ssds)):
            node = nodes[ idx % nodeLen ]
            node.addDevice( ssds[idx] )

        ifNames = res.getIFNames()
        ifAddrs = res.getIFAddrs()
        for idx in range(len(ifNames)):
            if idx == 0:
                continue
            for node in nodes:
                node.addInterface( ifNames[idx], ifAddrs[idx] )
            
        for node in nodes:
            self.addDockNode( node )

            if not self.isCfgCluster and node.svcRefector:
                if bool(node.ifs):
                    self.cfgCluster(node.ifs[0][1], node.basePort)
                else:
                    self.cfgCluster(ip, node.basePort)


if __name__ == '__main__':
    ''' Test this module here '''
    dcfg   = KdDcfg('668cebd6-32ab-44c0-a856-5a4f4fdb2dc4', 'test')
    tml1   = KdDNodeTemplate('DN-template1', 4000, services=[1, 1, 1],
            devices=['Disk1', 'Disk2'])
    tml2   = KdDNodeTemplate('DN-template2', 4000, devices=['Disk1', 'Disk2'])

    dcfg.addDNodeTml( tml1 )
    dcfg.addDNodeTml( tml2 )

    dhost1 = KdDHost('host1')
    dhost1.addDNode('DN-template1', 'DN1')
    dhost2 = KdDHost('host2')
    dhost1.addDNode('DN-template2', 'DN2')

    dcfg.addDHost( dhost1 )
    dcfg.addDHost( dhost2 )

    dcfg.write('test.xml')


