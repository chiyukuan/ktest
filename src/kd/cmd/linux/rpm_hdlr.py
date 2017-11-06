#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class RpmHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        return cmdCtx.cmdMsg.startswith("rpm -q ")

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.startswith("rpm -q ") or line.isspace():
                continue
            if line.endswith(' is not installed'):
                cmdCtx.setRC(RC.NOT_FOUND, line)
            else:
                cmdCtx.setRC(RC.OK, line)
                rslt = line
            break
        return rslt


if __name__ == '__main__':
    ''' Test this module here '''


