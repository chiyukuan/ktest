#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
from kd.util.logger  import getLogger
from kd.util.rc_msg  import RC
from kd.util.url     import Url
from kd.util.kspawn  import getUrlSess, getGdbSess
from kd.ep.tkcd_sess import TkcdSess
from kd.ep.local_sess import LocalSess
from kd.ep.cmd_ctx   import CmdCtx
from kd.ep.cmd_hdlr  import CmdHdlr

from kd.cmd.linux.lcmd_hdlr import LcmdHdlr

logger = getLogger(__name__)

def getTkcdCtx(url, dFN='/tmp/dFile'):
    if type(url) is str:
        url = Url.fromStr(url) ;
    sess = TkcdSess(url, dFN)
    try:
        sess.connect()
    except:
        return None
    else:
        return EpCtx(sess)

def getLinuxCtx(url, seps=None):
    if type(url) is str:
        url = Url.fromStr(url) ;
    if seps is None:
        seps = '[^\r\n ]*%s[^\#\$]*[#$][^ ]* ' % (url.shostname)
    sess = getUrlSess(url, seps)
    if sess is None:
        logger.error("Failed to create linux session") ;
        return None
    else:
        return EpCtx(sess)

def getLocalCtx():
    sess = LocalSess()
    return EpCtx(sess)

def getGdbCtx(url):
    sess = getGdbSess(url)
    return EpCtx(sess)


class EpCtx(object):
    ''' Endpoint context. The endpoint uses the session object to interact with
        remote entity.
    '''

    def __init__(self, sess):
        self.sess = sess
        self.cmdCtx = CmdCtx()

        self.cmdHdlrClasses = []
        classes = CmdHdlr.__subclasses__()

        for clazz in classes:
            self.cmdHdlrClasses.append(clazz)
            classes2 = clazz.__subclasses__()
            if classes2:
                classes.extend(classes2)

    def run(self, cmdMsg, timeout=-1, tryParse=True, seps=None, noRsp=False):
        '''
        Run this cmdMsg against this endpoint.
        '''
        self.cmdCtx.setRC(RC.OK)
        self.cmdCtx.cmdMsg = cmdMsg
        self.sess.sendline( cmdMsg )
        self.cmdCtx.rslt = None
        
        if noRsp:
            self.cmdCtx.setRC( RC.OK )
            return self.cmdCtx.rcMsg.rc

        rc, rspMsg = self.sess.expect(seps, timeout=timeout)

        if rc == RC.OK:
            self.cmdCtx.setRC( RC.OK )
            if isinstance( rspMsg,  basestring ):
                self.cmdCtx.rspMsg = rspMsg.strip().replace("\r", "")
            else:
                self.cmdCtx.rspMsg = rspMsg
            if tryParse:
                for clazz in self.cmdHdlrClasses:
                    if clazz.canParseRslt(self.cmdCtx):
                        self.cmdCtx.rslt = clazz.parseRslt(self.cmdCtx)
                        break

        else:
            self.cmdCtx.setRC( rc, rspMsg )
        return self.cmdCtx.rcMsg.rc

    def close(self):
        self.sess.close()

    def getSess(self):
        return self.sess

    def getCmdCtx(self):
        return self.cmdCtx

    def getRcMsg(self):
        return self.cmdCtx.rcMsg

    def getRC(self):
        return self.cmdCtx.rcMsg.rc

    def getRslt(self):
        return self.cmdCtx.rslt

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    #sess = getLinuxCtx( 'ssh://rkuan:password@ray-mac-c70' )
    urlStr = 'ssh://root:password@rayvm/'
    cmd    = '/bin/curl -X POST -H "Content-Type: application/xml" -d @/tmp/ktest_stage_container.xml http://localhost:5001/kodiak/api/broker/stage/container'
    cmd    = '/bin/curl http://rayvm:5001/kodiak/api/resources/tiles'

    sess = getLinuxCtx( urlStr )
    sess.run( cmd )
    print sess.cmdCtx
    #print "CmdCtx %s" % sess.cmdCtx

    #sess.run("echo $?")
    sess.close()

