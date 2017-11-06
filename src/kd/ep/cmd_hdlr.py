#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.util import must_override
from kd.util.logger import getLogger

logger = getLogger(__name__)

class CmdHdlr(object):
    ''' Command parser abstract class
    '''

    def __init__(self):
        pass

    @staticmethod
    @must_override
    def canParseRslt(cmdCtx):
        return False

    @staticmethod
    @must_override
    def parseRslt(cmdCtx):
        return None

if __name__ == '__main__':
    ''' Test this module here '''


