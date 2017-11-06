#! /usr/bin/env python

from lcmd_hdlr      import LcmdHdlr
from kd.util.rc_msg import RC

class SystemctlIsactive(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/systemctl is-active"):
            return True
        if cmdCtx.cmdMsg.startswith("systemctl is-active"):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/systemctl"):
                continue
            if line.startswith("systemctl"):
                continue

            rslt = True if line == 'active' else False
            break

        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    from kd.ep.cmd_ctx  import CmdCtx

    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "systemctl is-active kodiak-data-engine"
    cmdCtx.rspMsg = cmdCtx.cmdMsg + """ ....
active"""

    if SystemctlIsactive.canParseRslt(cmdCtx):
        cmdCtx.rslt = SystemctlIsactive.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"




