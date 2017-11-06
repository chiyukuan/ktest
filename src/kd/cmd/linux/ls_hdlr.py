#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class LsHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        return cmdCtx.cmdMsg.startswith("/bin/ls --color=none ")

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/ls ") or line.startswith("/bin/ls:"):
                continue

            if line.find("No such file or directory") >= 0:
                cmdCtx.setRC(RC.NOT_FOUND, line)
                break

            for name in line.split():
                if name.strip() != '':
                    if rslt is None:
                        rslt = [name]
                    else:
                        rslt.append(name)
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "/bin/ls --color=none /dev"
    cmdCtx.rspMsg = """autofs cpu_dma_latency input mem pts sr0 tty14
tty24  tty34  tty44  tty54  tty7 usbmon1  vcsa"""

    if LsHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = LsHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"

