#! /usr/bin/env python

from lcmd_hdlr      import LcmdHdlr

class SystemctlStatus(LcmdHdlr):

    def __init__(self):
        pass

    @staticmethod
    def canParseRslt(cmdCtx):
        if cmdCtx.cmdMsg.startswith("/bin/systemctl status"):
            return True
        if cmdCtx.cmdMsg.startswith("systemctl status"):
            return True
        return False

    @staticmethod
    def parseRslt(cmdCtx):
        rslt = None

        for line in cmdCtx.rspMsg.splitlines():
            if line == "" or line.isspace():
                continue
            if line.startswith("/bin/systemctl"):
                continue
            if line.startswith("systemctl"):
                continue

            if "Active:" not in line:
                continue

            tokens = line.split()
            if tokens[1] != 'disk':
                continue
            if rslt is None:
                rslt = []
            rslt.append( (tokens[-1], tokens[0][1:-1]) )
        return rslt

if __name__ == '__main__':
    ''' Test this module here '''
    from kd.ep.cmd_ctx  import CmdCtx

    cmdCtx        = CmdCtx()
    cmdCtx.cmdMsg = "systemctl status kodiak-data-engine"
    cmdCtx.rspMsg = """systemctl status kodiak-data-engine ....
   Loaded: loaded (/usr/lib/systemd/system/kodiak-data-engine.service; disabled; vendor preset: disabled)
      Active: inactive (dead) """

    if SystemctlStatus.canParseRslt(cmdCtx):
        cmdCtx.rslt = SystemctlStatus.parseRslt(cmdCtx)
        print "canParse:\n %s" % cmdCtx
    else:
        print "Failed to parse it!!!"



