
''' ------------------------|  Python SOURCE FILE  |------------------------
'''

from kd.util.enum import enum

TKCD_CMD_TYPE = enum( ['READ',         1],
                      ['WRITE',        2],
                      ['DEV_ADD',     11],
                      ['DEV_DEL',     13],
                      ['DEV_ERR',     14],
                      ['DEV_ERR_IO',  15],
                      ['NODE_BIND',   22],
                      ['NODE_UNBIND', 23],
                      ['DOCK_BIND',   29],
                      ['DOCK_UNBIND', 30],
                      ['DEL_PANEL',   25] )

TKCD_PROT_TYPE = enum( ['P_none', 0],
                       ['P_4x1_32k',      1],
                       ['P_8x1_8k',       2],
                       [        'P__1x1', 0 + (3 << 4)],
                       [        'P__1x2', 0 + (4 << 4)],
                       ['P_4x1_32k__1x1', 1 + (3 << 4)],
                       ['P_8x1_8k__1x1',  2 + (3 << 4)],
                       ['P_4x1_32k__1x2', 1 + (4 << 4)],
                       ['P_8x1_8k__1x2',  2 + (4 << 4)] 
                     )

def hasDockProt( pTypeEnum ):
    return pTypeEnum.getVal() >= (1 << 4)
