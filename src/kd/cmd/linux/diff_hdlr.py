#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class DiffHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        return cmdCtx.cmdMsg.startswith("diff -q ")

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.startswith("diff -q ") or line.isspace():
                continue
            cmdCtx.setRC(RC.MISMATCH, line)
            break
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "diff -q new.txt old.txt"
    cmdCtx.rspMsg = """Files new.txt and old.txt differ"""

    if DiffHdlr.canParseRslt(cmdCtx):
        print "canParse"
        DiffHdlr.parseRslt(cmdCtx)
        print cmdCtx
    else:
        print "Failed to parse it!!!"


