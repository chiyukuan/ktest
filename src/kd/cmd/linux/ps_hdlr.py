#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class PsHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/ps aux | /bin/grep "):
            return True
        if cmdCtx.cmdMsg.startswith("ps aux | grep "):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/ps ") or line.startswith("ps "):
                continue
            if 'grep' in line:
                continue

            words = line.split()
            if rslt == None:
                rslt = [ words[1] ]
            else:
                rslt.append(words[1])

        if rslt == None:
            cmdCtx.setRC(RC.NOT_FOUND)
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "ps aux | grep --color=never kdpkd.*1"

    cmdCtx.rspMsg = """\
root      6647  0.2  1.7 697336 32400 ?        Ssl  01:06   0:00 node ./kdpkd_main.js kdpkd.myDock.1
root      8445  0.0  0.0 112644   996 pts/0    S+   01:13   0:00 grep --color=auto --color=never kdpkd.*1
"""

    if PsHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = PsHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"





