#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.util   import must_override
from kd.util.rc_msg import RC
from kd.ep.cmd_hdlr import CmdHdlr
from kd.ep.cmd_ctx  import CmdCtx


class LcmdHdlr(CmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("echo $?"):
            return True
        return False


    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None
        if cmdCtx.cmdMsg.startswith("echo $?"):
            for line in cmdCtx.rspMsg.splitlines():
                if line == "" or line == cmdCtx.cmdMsg or line.isspace():
                    continue
                if line == "0":
                    cmdCtx.setRC(RC.OK)
                else:
                    rslt = line
                    cmdCtx.setRC(RC.ERROR,
                        "Fail to execute previous cmd") ;
                break
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "echo $?"
    cmdCtx.rspMsg = """0"""

    if LcmdHdlr.canParseRslt(cmdCtx):
        print "canParse"
        LcmdHdlr.parseRslt(cmdCtx)
        print cmdCtx
    else:
        print "Failed to parse it!!!"

