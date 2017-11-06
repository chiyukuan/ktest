#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from enum import enum

RC = enum('OK', 'ERROR', 'TIMEOUT', 'WARNING', 'MISMATCH', 'NOT_YET', 'CONTINUE', 'NOT_FOUND')


class RcMsg(object):
    ''' Return code and its message '''

    def __init__(self, rc = RC.OK, msg = None):
        self.rc = rc
        self.msg = msg

    def setRC(self, rc, msg=None):
        self.rc = rc
        self.msg = msg

    def __str__(self):
        if self.msg and self.msg != "":
            return "%s-'%s'" % (self.rc, self.msg)
        else:
            return self.rc.__repr__()

    __repr__ = __str__

if __name__ == '__main__':
    rcMsg = RcMsg(RC.ERROR, "has error")
    print rcMsg


