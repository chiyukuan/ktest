#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr

class PvdisplayHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/usr/sbin/pvdisplay -c"):
            return True
        if cmdCtx.cmdMsg.startswith("pvdisplay -c"):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/usr/sbin/pvdisplay"):
                continue
            if line.startswith("pvdisplay"):
                continue

            rslt = line.strip().split(':')
        return rslt

if __name__ == '__main__':
    from kd.ep.cmd_ctx  import CmdCtx

    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "/usr/sbin/pvdisplay -c"
    cmdCtx.rspMsg = """/usr/sbin/pvdisplay ....
  /dev/sda2:centos_kodiak-cube2-c71-br4:66082816:-1:8:8:-1:4096:8066:11:8055:82FBVl-xqTS-C9Ja-m5J7-xhaw-bgeL-9eQ6Q9"""

    if PvdisplayHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = PvdisplayHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"


