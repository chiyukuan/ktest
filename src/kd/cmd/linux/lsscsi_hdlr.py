#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr

class LsscsiHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/lsscsi"):
            return True
        if cmdCtx.cmdMsg.startswith("lsscsi"):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/lsscsi"):
                continue
            if line.startswith("lsscsi"):
                continue

            tokens = line.split()
            if tokens[1] != 'disk':
                continue
            if tokens[2] == 'iDRAC':
                continue

            if rslt is None:
                rslt = []
            rslt.append( (tokens[-1], tokens[0][1:-1]) )
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    from kd.ep.cmd_ctx  import CmdCtx

    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "/bin/lsscsi"
    cmdCtx.rspMsg = """/bin/lsscsi ....
[0:0:0:0]    cd/dvd  QEMU     QEMU DVD-ROM     1.5.  /dev/sr0
[2:0:0:0]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sda
[2:0:0:1]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdi
[2:0:0:2]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdg
[2:0:0:3]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sde
[2:0:0:4]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdc
[2:0:0:5]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdh
[2:0:0:6]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdf
[2:0:0:7]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdd
[2:0:0:8]    disk    QEMU     QEMU HARDDISK    1.5.  /dev/sdb"""

    if LsscsiHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = LsscsiHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"



