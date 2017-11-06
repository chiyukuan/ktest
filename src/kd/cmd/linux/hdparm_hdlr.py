#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.util.rc_msg import RC

class HdparmHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/usr/sbin/hdparm "):
            return True
        if cmdCtx.cmdMsg.startswith("hdparm "):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt       = None
        detailOpt  = False
        setPassOpt = False
        eraseOpt   = False

        if "-I" in cmdCtx.cmdMsg:
            detailOpt = True
            frozenState    = True
            notSupport     = True
            securityEnable = False
        elif "--security-set-pass" in cmdCtx.cmdMsg:
            setPassOpt = True
            securityEnable = False
        elif "--security-erase" in cmdCtx.cmdMsg:
            eraseOpt = True
            

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/usr/sbin/hdparm "):
                continue
            if line.startswith("hdparm "):
                continue

            if detailOpt:
                if "frozen" in line and "not" in line:
                    frozenState = False
                if "supported: enhanced erase" in line:
                    notSupport  = False
                if "enabled" in line and "not" not in line:
                    securityEnable = True
            elif eraseOpt:
                if "real" in line:
                    cmdCtx.setRC(RC.OK)
                    rslt = line

        if detailOpt:
            rslt = (frozenState, notSupport, securityEnable)
            if notSupport:
                cmdCtx.setRC(RC.ERROR, "Enhanced erase is not supported")
            elif frozenState:
                cmdCtx.setRC(RC.ERROR, "SSD in frozen state")
            else:
                cmdCtx.setRC(RC.OK)

        elif setPassOpt:
            if securityEnable:
                cmdCtx.setRC(RC.OK)
            else:
                cmdCtx.setRC(RC.ERROR, "Failed to enable security feature")

        return rslt

if __name__ == '__main__':
    from kd.ep.cmd_ctx  import CmdCtx

    ''' Test this module here '''
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



