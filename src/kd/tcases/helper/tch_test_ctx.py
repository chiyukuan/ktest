#! /usr/bin/env python

from kd.tfwk.test_case import TestCase

class TchTestCtx(TestCase):

    def __init__(self, cmd, varName, value=None):
        if 'set' == cmd:
            super(TchTestCtx, self).__init__(None, 'Set test context variable %s to %s' % (varName, value))
            self.addStep("set variable", self._setVariable, opq=[varName, value])

    @classmethod
    def allTestCases(cls):
        return None

    def _prepare(self, step):
        return

    def _tearDown(self, step):
        return

    def _setVariable(self, step):
        varName, value = step.opq
        print value
        TestCase.setParam( varName, value )

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__


