#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import re
from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class DdHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        return cmdCtx.cmdMsg.startswith("/bin/dd ")

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/dd"):
                if "Input/output error" in line:
                    cmdCtx.setRC(RC.ERROR, line)
                    break
                continue
            if line.endswith('records in') or line.endswith('records out'):
                continue
            if "bytes (" not in line:
                continue
            
            m = re.findall('([-+]?\d+[\.]?\d*)', line)
            rslt = [int(m[0]), float(m[2])]
            break

        return rslt


if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "/bin/dd new.txt old.txt"
    cmdCtx.rspMsg = """/bin/dd if=/dev/zero of=/dev/kdblk0 bs=8192 seek=0 cou nt=1 oflag=direct,seek_bytes
/bin/dd: error writing /dev/kdblk0: Input/output error
1+0 records in
0+0 records out
0 bytes (0 B) copied, 29.5568 s, 0.0 kB/s"""

    if DdHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = DdHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"

