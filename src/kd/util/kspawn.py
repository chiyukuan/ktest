#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
import pexpect
import re

from kd.util.logger import getLogger
from kd.util.url import Url
from kd.util.rc_msg import RC

logger = getLogger(__name__)

def getUrlSess(url, seps, maxRetry=0):
    kspawn = Kspawn(url, seps)
    if kspawn.start(maxRetry):
        return kspawn
    else:
        return None

def getGdbSess(url):
    kspawn = Kspawn(url, '\(gdb\)')
    if kspawn.start(0):
        return kspawn
    else:
        return None


def execUrlSess(url, maxRetry=0, scpFrom=None, scpTo=None):
    kspawn = Kspawn(url, pexpect.EOF)
    if kspawn.start(maxRetry, timeout=7200, scpFrom=scpFrom, scpTo=scpTo):
        return True
    else:
        return False

class Kspawn(pexpect.spawn):
    '''
    Proxy object of pexpect.spawn to inject the costomized features.
    '''

    def __init__(self, url, seps, timeout=21600, maxread=2000, searchwindowsize=None,
                 cwd=None, env=None):
        pexpect.spawn.__init__(self, None, timeout=timeout, maxread=maxread,
                               searchwindowsize=searchwindowsize, logfile=self,
                               cwd=cwd, env=env)
        self.url = url
        self.seps = seps
        self.sending = False
        self.sendCmd = ''
        

    def write(self, *args, **kwargs):
        content = args[0]
        # let's ignore other PARAMS, PEXPECT only use one ARG AFAIK
        if content in [' ', '', '\n', '\r', '\r\n']:
            return  # don't log empty lines
        for eol in ['\r\n', '\r', '\n']:
            # remove ending EOL, the logger will add it later
            content = re.sub('\%s$' % eol, '', content)
        if self.sending:
            return logger.debug("<=={: :_CMD_@%s: %s :}",
                                self.url.shostname, content)
        else:
            return logger.debug("==>{: :_CMD_RST_@%s: \n%s\n:}\n",
                                self.url.shostname, content)

    def flush(self):
        pass

    def send(self, sendCmd):
        self.sendCmd = sendCmd
        self.sending = True
        cnt = super(Kspawn, self).send( sendCmd )
        self.sending = False
        return cnt

    def sendline(self, s=''):
        return self.send("%s\r" % s)

    def start(self, maxRetry, timeout=120, scpFrom=None, scpTo=None):
        """ logs this user into the given server. """

        cmd = None
        if self.url.protocol == "ssh":
            if self.url.port is not None:
                cmd = "ssh -l %s %s -p %d" % (self.url.user, self.url.hostname, self.url.port)
            else:
                cmd = "ssh -l %s %s" % (self.url.user, self.url.hostname)
        elif self.url.protocol == "telnet":
            cmd = "telnet -l %s %s" % (self.url.user, self.url.hostname)
        elif self.url.protocol == "gdb":
            cmd = "gdb %s %s" % (self.url.filename, self.url.query)
        elif self.url.protocol == "scp":
            if scpTo is not None:
                if self.url.port is not None:
                    cmd = "scp -P %d %s@%s:%s %s" % (self.url.port, self.url.user, self.url.hostname, self.url.filename, scpTo)
                else:
                    cmd = "scp %s@%s:%s %s" % (self.url.user, self.url.hostname, self.url.filename, scpTo)
            elif scpFrom is not None:
                if self.url.port is not None:
                    cmd = "scp -P %d %s %s@%s:%s" % (self.url.port, scpFrom, self.url.user, self.url.hostname, self.url.filename)
                else:
                    cmd = "scp %s %s@%s:%s" % (scpFrom, self.url.user, self.url.hostname, self.url.filename)
            else:
                return False
        else:
            return False

        logger.debug("execute the '%s' cmd, seps = '%s'", cmd, self.seps)
        
        self.sendCmd = cmd
        pexpect.spawn._spawn( self, cmd )

        while True:
            rc = super(Kspawn, self).expect(['(?i)password',
                              '(?i)are you sure you want to continue connecting',
                              '(?i)key verification failed',
                              pexpect.TIMEOUT,
                              self.seps,
                              ], timeout=timeout)
            if rc == 0:
                self.sendline(self.url.password)
            elif rc == 1:
                self.sendline('yes')
            elif rc == 2:
                self.kill(0)
                os.popen('rm -f ~/.ssh/known_hosts')
                return False
            elif rc == 3:
                if maxRetry == 0:
                    return False
                maxRetry -= 1
            elif rc == 4:
                return True
            else:
                self.kill(0)

    def close(self):
        """ Send the exit to remote shell. If there are stopped jobs then
        this automatically sends exit twice. """

        if self.url.protocol == "gdb":
            exitCmd = "quit"
        else:
            exitCmd = "exit"
        self.sendline(exitCmd)
        index = self.expect([pexpect.EOF, "(?i)there are stopped jobs"])
        if index == 1:
            self.sendline(exitCmd)
            self.expect(pexpect.EOF)
        super(Kspawn, self).close()

    def expect(self, seps=None, timeout=-1):
        if seps is None:
            patterns = self.seps
        else:
            patterns = seps
        patternTOutIdx = len( patterns )
        expectRC = super(Kspawn, self).expect(patterns, timeout=timeout)

        if expectRC == patternTOutIdx:
            return RC.ERROR, "Timeout to execute command, '%s' at %s" % (
                             self.sendCmd, self.url)
        else:
            return RC.OK, self.before


if __name__ == '__main__':
    ''' Test this module here '''

    
    #url = Url.fromStr("ssh://root:kodiak@kodiak-cube2-c71-utest")
    #urlSess = getUrlSess( url, 'kodiak-cube2-c71-utest ' )
    #urlSess.close()
    url = Url.fromStr("gdb://localhost//root/gitwork/KodiakContainer/usr/src/kdtkd/kdtkcd/OBJS/kdtkcd?41617")
    sess = getGdbSess(url)
    sess.sendline('set confirm off')
    print sess.expect()
    sess.sendline('print TkcTx::txCB->txFreeList.cnt')
    print sess.expect()
    sess.sendline('quit')
    #url.dstFilename = "abcd"
    #print execUrlSess(url, scpTo="/home/rkuan/aa.bachrc")

