#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import ConfigParser
import os
import datetime
import platform
from   kd.util.logger import getLogger
import kd.tcases
from kd.util.environ import Environ

logger = getLogger(__name__)

class TestCtx(object):
    ''' Test context contains the attributes of all test cases '''

    def __init__(self, cfgFile):
        ''' Read the configuration file '''
        self.config = ConfigParser.ConfigParser()
        self.config.read(cfgFile)
        self.params = dict()
        self.desc   = "Run test suite"  # default description for all test case
        self.whitelist = []
        self.blacklist = []

    def loadTestSuite(self, tsuite):
        for pair in self.config.items(tsuite):
            if   pair[0] == 'test_suite':
                incName = 'test_suite_' + pair[1]
                # if tsuiteForce is None or tsuite == tsuiteForce:
                self.loadTestSuite( incName )

            elif pair[0] == 'include_test_bench':
                if pair[1].startswith('eval('):
                    incName = 'test_bench::' + eval(pair[1][5:-1])
                else:
                    incName = 'test_bench::' + pair[1]
                self.loadTestSuite( incName )

            elif pair[0] == "desc":
                self.desc = pair[1]

            elif pair[0] == "whitelist":
                self.whitelist = pair[1]

            elif pair[0] == "blacklist":
                self.blacklist = pair[1]

            elif pair[0] == "work_dir" or pair[0] == "default_work_dir":
                homeDir = os.path.expanduser('~')
                dtime   = datetime.datetime.now().strftime("%y%m%d_%H")
                path    = pair[1]
                path    = path.replace('<HOME>', homeDir)
                path    = path.replace('<TIME>', dtime)
                path    = path.replace('<SUITE>', Environ.TestSuit)
                path    = path.replace('<WDIR_TAG>', Environ.WDirTag)
                try:
                    os.makedirs(path)
                except OSError as exc:
                    if not os.path.isdir(path):
                        raise
                latest = "%s/.__latest__" % path[:(path.rfind('/'))]
                try:
                    os.unlink(latest)
                except:
                    pass

                os.symlink(path, latest)
                self.params[pair[0]] = path
            else:
                self.params[pair[0]] = pair[1]


    def loadTestCtx(self, tsuiteForce):

        self.loadTestSuite( 'test_suite' )
        if tsuiteForce is not None:
            tsuiteForce = 'test_suite_' + tsuiteForce
            self.loadTestSuite( tsuiteForce )

        return self.desc, self.whitelist, self.blacklist

    def listTestSuite(self, prefix=None):
        if prefix is not None:
            prefix = 'test_suite_%s' % prefix
        else:
            prefix = 'test_suite_'

        for section in self.config.sections():
            if not section.startswith(prefix):
                continue
            if section.startswith('test_suite_setup_'):
                continue

            print " - %-25s : %s" % (section[11:],
                    self.config.get(section, 'desc'))

    def getParam(self, name):
        name2 = '_' + name
        if name2 in self.params:
            return self.params[name2]
        else:
            return None if name not in self.params else self.params[name]

    def getParamExact(self, name):
        return None if name not in self.params else self.params[name]

    def setParam(self, name, value):
        self.params[name] = value

    def checkParam(self, name, value):
        return True if self.getParam(name) == value else False

    def hasParam(self, name):
        ret = False
        while True:
            if self.params is None:
                break
            if name not in self.params and '_' + name not in self.params:
                break
            ret = True
            break
        return ret

    def popParam(self, name):
        if name in self.params:
            self.params.pop(name, None)

    def __str__(self):
        return self.params.__repr__()

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    testCtx = TestCtx( Environ.CFG_FILE_NAME )
    testCtx.loadTestCtx(None)
    print testCtx


