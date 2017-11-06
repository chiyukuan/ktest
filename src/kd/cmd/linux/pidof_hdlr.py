#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC


class PidofHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/usr/sbin/pidof "):
            return True
        elif cmdCtx.cmdMsg.startswith("pidof "):
            return True
        else:
            return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/usr/sbin/pidof  ") or line.startswith("pidof "):
                continue

            for name in line.split():
                if name.strip() != '':
                    if rslt is None:
                        rslt = [ int(name) ]
                    else:
                        rslt.append(int(name))
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "pidof kdtkcd"
    cmdCtx.rspMsg = """1234 5678"""

    if PidofHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = PidofHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"



