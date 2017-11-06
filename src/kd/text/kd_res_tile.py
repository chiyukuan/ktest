#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from xml.dom import minidom

logger = getLogger(__name__)

class KdResTile(object):

    def __init__(self, resTile, isFile=True):
        if isFile:
            self.doc = minidom.parse(resTile)
        else:
            self.doc = minidom.parseString( resTile )

    def _getCnt(self, tag, szByte=True, nodeId=None, tileType=1):
        tileCnt = 0
        dnNodes = self.doc.getElementsByTagName('dn')
        for dnNode in dnNodes:
            if nodeId is not None:
                idNodes = dnNode.getElementsByTagName('dock_node_id')
                if int(idNodes[0].childNodes[0].nodeValue) != nodeId:
                    continue
            trNodes = dnNode.getElementsByTagName('tile_tray')
            for trNode in trNodes:
                if tileType is not None:
                    tyNodes = trNode.getElementsByTagName('tile_type')
                    if int(tyNodes[0].childNodes[0].nodeValue) != tileType:
                        continue

                alNodes = trNode.getElementsByTagName(tag)
                for alNode in alNodes:
                    if szByte:
                        szNodes = trNode.getElementsByTagName('tile_size')
                        tileSz = int(szNodes[0].childNodes[0].nodeValue)
                        tileCnt += tileSz * int(alNode.childNodes[0].nodeValue)

                    else:
                        tileCnt += int(alNode.childNodes[0].nodeValue)
        return tileCnt

    def getAllocTiles(self, nodeId=None, tileType=1):
        return self._getCnt('alloc_tiles', False, nodeId, tileType)

    def getAllocTileSize(self, nodeId=None, tileType=1):
        return self._getCnt('alloc_tiles', True, nodeId, tileType)

    def getFreeTiles(self, nodeId=None, tileType=1):
        return self._getCnt('free_tiles', False, nodeId, tileType)

    def getFreeTileSize(self, nodeId=None, tileType=1):
        return self._getCnt('free_tiles', True, nodeId, tileType)

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

    resTileStr='''<?xml version="1.0" encoding="UTF-8"?>
<dock_tiles>
        <dn>
                <dock_node_id>1</dock_node_id>
                <dock_plate_id>1</dock_plate_id>
                <virtual_rack_id>1</virtual_rack_id>
                <tile_tray>
                        <tile_type>0</tile_type>
                        <tile_size>1073741824</tile_size>
                        <alloc_tiles>0</alloc_tiles>
                        <free_tiles>0</free_tiles>
                </tile_tray>
                <tile_tray>
                        <tile_type>1</tile_type>
                        <tile_size>1073741824</tile_size>
                        <alloc_tiles>25</alloc_tiles>
                        <free_tiles>204275</free_tiles>
                </tile_tray>
                <tile_tray>
                        <tile_type>2</tile_type>
                        <tile_size>1073741824</tile_size>
                        <alloc_tiles>0</alloc_tiles>
                        <free_tiles>0</free_tiles>
                </tile_tray>
        </dn>
</dock_tiles>
'''
    #resTile = KdResTile('/tmp/ktest_res_tiles.xml')
    resTile = KdResTile(resTileStr, isFile=False)
    print "Alloc Tile: %d" % resTile.getAllocTiles()
    print "Alloc Tile Size: %d" % resTile.getAllocTileSize()
    print "Free Tile: %d" % resTile.getFreeTiles()
    print "Free Tile Size: %d" % resTile.getFreeTileSize()



