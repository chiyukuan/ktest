#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from subprocess import PIPE, Popen
from kd.util.logger import getLogger
from kd.util.rc_msg import RC

logger = getLogger(__name__)

class LocalSess(object):

    def __init__(self):
        self.cmd = None

    def connect(self):
        pass

    def close(self):
        pass

    def send(self, cmd):
        self.cmd = cmd

    sendline = send

    def expect(self, seps=None, timeout=-1):
        logger.debug("<=={: :_CMD_@localhost: %s :}", self.cmd)
        process = Popen(args=self.cmd, stdout=PIPE, shell=True)
        rsp     = process.communicate()[0]
        logger.debug("==>{: :_CMD_RST_@localhost: \n%s\n:}\n", rsp)
        return RC.OK, rsp

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    sess = LocalSess()
    sess.connect()
    sess.send('ls')
    print sess.expect()
    sess.close()


