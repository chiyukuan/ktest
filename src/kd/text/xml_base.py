#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from xml.dom import minidom

class XmlBase(object):

    def __init__(self, inXmlFN=None):
        if inXmlFN is not None:
            self.doc = minidom.parse( inXmlFN )

    def _pairToXml(self, pElm, pairs):
        ''' Convert the pairs into xml element under pElm'''
        for pair in pairs:
            elm = self.doc.createElement(pair[0])
            if pair[1] is not None:
                if isinstance( pair[1], int ):
                    elm.appendChild( self.doc.createTextNode( "%d" % pair[1]) )
                else:
                    elm.appendChild( self.doc.createTextNode(pair[1]) )

            pElm.appendChild( elm )

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


