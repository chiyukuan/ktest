#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class LsmodHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("lsmod "):
            return True
        elif cmdCtx.cmdMsg.startswith("/usr/sbin/lsmod "):
            return True
        else:
            return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/usr/sbin/lsmod ") or line.startswith("lsmod "):
                continue

            print line
            words = line.split()
            rslt = [words[0], int(words[2])]
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "lsmod | grep --color=never kodiak"
    cmdCtx.rspMsg = """lsmod | grep --color=never kodiak
kodiak                118041  0
"""

    if LsmodHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = LsmodHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"



