#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from lcmd_hdlr      import LcmdHdlr
from kd.ep.cmd_ctx  import CmdCtx
from kd.util.rc_msg import RC

class MountHdlr(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/mount -l "):
            return True
        if cmdCtx.cmdMsg.startswith("mount -l "):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/mount ") or line.startswith("mount "):
                continue

            words = line.split()
            devInfo = [words[0], words[2], words[4]]
            if rslt is None:
                rslt = [ devInfo ]
            else:
                rslt.append( devInfo )
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "mount -l | grep docknode"
    cmdCtx.rspMsg = """mount -l | grep docknode
/dev/sdb on /kodiak/dock/myDock/docknode/1/mnt/0 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
/dev/sdc on /kodiak/dock/myDock/docknode/1/mnt/1 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
/dev/sdd on /kodiak/dock/myDock/docknode/1/mnt/2 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
/dev/sde on /kodiak/dock/myDock/docknode/1/mnt/3 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
/dev/sdg on /kodiak/dock/myDock/docknode/1/mnt/4 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
/dev/sdh on /kodiak/dock/myDock/docknode/1/mnt/5 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
/dev/sdi on /kodiak/dock/myDock/docknode/1/mnt/6 type xfs (rw,relatime,seclabel,attr2,inode64,noquota)"""

    if MountHdlr.canParseRslt(cmdCtx):
        cmdCtx.rslt = MountHdlr.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"

