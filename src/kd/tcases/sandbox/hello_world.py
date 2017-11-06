#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tfwk.test_case import TestCase
from kd.util.rc_msg import RC

logger = getLogger(__name__)

class HelloWorld(TestCase):
    ''' Hello world test case '''

    def __init__(self, desc, names):
        super(HelloWorld, self).__init__(None, desc)
        self.balckList = ['Ray']
        self.panicList = ['Javascript']
        self.names = names
        self.name = None
        for name in names:
            self.addStep("Welcome %s" % name, self._welcome)

    def _prepare(self, step):
        step.setRC( RC.OK)

    def _tearDown(self, step):
        step.setRC( RC.OK)

    def _welcome(self, step):
        self.name = self.names.pop(0)
        if self.name in self.names:
            logger.info("Hello %s", self.name)
            step.setRC(RC.OK, "Hello %s" % self.name)

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

    @classmethod
    def allTestCases(cls):
        tcases = []
        tcases.append( cls("Hello Names",    ['Amy', 'Constance', 'Michelle', 'Ray'] ))
        tcases.append( cls("Hello Language", ['C', 'C++', 'Javascript', 'Python']))
        tcases.append( cls("Hello Letters",  ['aA', 'bB', 'cC', 'dD']))
        return tcases

if __name__ == '__main__':
    ''' Test this module here '''


