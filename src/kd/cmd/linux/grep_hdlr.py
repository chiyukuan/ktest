#! /usr/bin/env python

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class GrepHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/grep "):
            return True
        if cmdCtx.cmdMsg.startswith("/bin/egrep "):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/grep ") or line.startswith("/bin/egrep "):
                continue
            if rslt == None:
                rslt = [ line ]
            else:
                rslt.append(line)
        if rslt == None:
            cmdCtx.setRC(RC.NOT_FOUND)
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''


