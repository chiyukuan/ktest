#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.enum import enum
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.tfwk.test_case import TestCase
from kd.tcases.tc_bench import TcBench
from kd.tcases.tc_base  import TcBase
from kd.text.kd_res import KdRes

logger = getLogger(__name__)

IO_TYPE = enum('WRITE', 'READ', 'WRITE_AND_READ')

class TcNomadDev(object):
    def __init__(self, name, sz=None):
        self.name = name
        self.sz   = sz      # size in byte
        self.dic  = {}
        self.ltnc1w = None
        self.ltnc2w = None
        self.ltncAw = None
        self.ltnc1r = None
        self.ltncAr = None

class TcNomadBase(TcBase):

    def __init__(self, desc):
        super(TcNomadBase, self).__init__(desc)

    @classmethod
    def allTestCases(cls):
        return []


    def _prepare(self, step, appHost=True):
        super(TcNomadBase, self)._prepare(step, appHost=appHost, dockHost=not appHost)

if __name__ == '__main__':
    ''' Test this module here '''


