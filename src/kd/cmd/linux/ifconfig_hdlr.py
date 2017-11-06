#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr

class IfconfigHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/usr/sbin/ifconfig -s"):
            return True
        if cmdCtx.cmdMsg.startswith("ifconfig -s"):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None
        virbrOnly = False

        if "virbr" in cmdCtx.rspMsg:
            virbrOnly = True

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/usr/sbin/ifconfig"):
                continue
            if line.startswith("ifconfig"):
                continue
            # skip virbr0 for libvirtd
            if line.startswith("virbr0"):
                continue
            '''
            if virbrOnly:
                if not line.startswith("virbr"):
                    continue
            '''
            if line.startswith("eth")  or \
               line.startswith("ens")  or \
               line.startswith("enp")  or \
               line.startswith("eno")  or \
               line.startswith("virbr"):

                tokens = line.split()
                
                if rslt is None:
                    rslt = []
                rslt.append( tokens[0] )
        return rslt

if __name__ == '__main__':
    from kd.ep.cmd_ctx  import CmdCtx

    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "/usr/sbin/ifconfig -s"
    cmdCtx.rspMsg = """/usr/sbin/ifconfig -s ....
Iface      MTU    RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP TX-OVR Flg
eth0      1500   299706     75      0 0         15949      0      0      0 BMRU
eth1      1500        0      0      0 0             0      0      0      0 BMU
eth2      1500   132601      0      0 0          8273      0      0      0 BMRU
eth3      1500        0      0      0 0             0      0      0      0 BMU
lo       65536       10      0      0 0            10      0      0      0 LRU
virbr0    1500 29749044      0      0 0       7320954      0      0      0 BMRU
virbr1    1500       10      0      0 0             9      0      0      0 BMRU
virbr2    1500   124383      0      0 0            35      0      0      0 BMRU
virbr3    1500       10      0      0 0             9      0      0      0 BMRU
vnet0     1500    11423      0      0 0        264318      0      0      0 BMRU
vnet1     1500       10      0      0 0            16      0      0      0 BMRU
vnet2     1500       10      0      0 0        123947      0      0      0 BMRU
vnet3     1500       10      0      0 0            16      0      0      0 BMRU
vnet4     1500 29517285      0      0 0      58859685      0      0      0 BMRU
vnet5     1500        0      0      0 0            19      0      0      0 BMRU
vnet6     1500        0      0      0 0        123954      0      0      0 BMRU
vnet7     1500        0      0      0 0            19      0      0      0 BMRU"""

    if IfconfigHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = IfconfigHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"



