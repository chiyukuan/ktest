#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class GcmdHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("print "):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("print "):
                continue
            words = line.split('=')
            rslt = words[1].strip()
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "print aaa"
    cmdCtx.rspMsg = """$65997 = 65996"""

    if GcmdHdlr.canParseRslt(cmdCtx):
        print "canParse"
        cmdCtx.rslt = GcmdHdlr.parseRslt(cmdCtx)
        print cmdCtx
    else:
        print "Failed to parse it!!!"



