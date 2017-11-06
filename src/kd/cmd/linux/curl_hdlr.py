#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import re
from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class CurlHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/curl -X POST"):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/curl "):
                continue
            if '<h1>' not in line:
                continue

            cmdCtx.rcMsg.rc = RC.ERROR
            m = re.search(r'<h1>(.*)</h1>', cmdCtx.rspMsg)
            rslt = m.group(1)
            break
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''


