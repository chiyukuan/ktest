#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom.minidom import Document

class KdHostBinding(object):

    def __init__(self):
        self.hosts = []
        self.docGen = False

    def addHost(self, name, ip=None, mac=None, fqdn=None):
        self.hosts.append( [name, ip, mac, fqdn] )

    def _genXml(self, doc=None, pElm=None):
        if self.docGen:
            return
        # create new doc
        if doc is not None and pElm is not None:
            self.doc  = doc
            self.root = pElm
        else:
            self.doc    = Document()
            self.root   = self.doc.createElement('host_binding')
            self.doc.appendChild( self.root )

        for host in self.hosts:
            hElm = self.doc.createElement('host')

            for pair in ( ('name',   host[0]),
                          ('ipaddr', host[1]),
                          ('mac',    host[2]),
                          ('fqdn',   host[3]),
                        ):

                elm = self.doc.createElement(pair[0])
                if pair[1] is not None:
                    if isinstance( pair[1], int ):
                        elm.appendChild( self.doc.createTextNode( "%d" % pair[1]) )
                    else:
                        elm.appendChild( self.doc.createTextNode(pair[1]) )
                hElm.appendChild( elm )
            self.root.appendChild( hElm )

        self.docGen = True


    def write(self, filename):
        self._genXml()
        # write doc
        file_handle = open(filename,"wb")
        self.doc.writexml(file_handle, addindent="    ",
                                       newl="\n", encoding="utf-8")
        file_handle.close()

    def __str__(self):
        self._genXml()
        return self.doc.toprettyxml(indent="    ", encoding="utf-8")

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

    hbinding = KdHostBinding()
    hbinding.addHost('host1', '172.16.13.128')
    hbinding.addHost('host2', '172.16.13.129', '00:0c:29:8c:4c:92')
    hbinding.addHost('DN1',   '172.16.13.128')
    hbinding.addHost('DN2',   '172.16.13.129')
    hbinding.addHost('host3', fqdn='www.google.com')
    hbinding.write('test.xml')


