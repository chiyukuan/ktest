#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tfwk.test_case import TestCase

logger = getLogger(__name__)

class TestSet(TestCase):

    def __init__(self, desc):
        super(TestSet, self).__init__(None, desc)

    @classmethod
    def allTestCases(cls, testSet):
        classes = [testSet]
        tcaseSpecs = testSet._getTestSpecs()
        if bool(tcaseSpecs):
            for spec in tcaseSpecs:
                tmp = TestSet.genTestCasesBySpec(spec)
                classes.extend( tmp )

        return classes

    def _prepare(self, tstep):
        return

    def _tearDown(self, tstep):
        return

    @classmethod
    def genTestCasesBySpec(cls, spec):
        if type(spec) is type:
            tcases = spec.allTestCases()
        elif isinstance( spec, TestSet ):
            tcases = spec.allTestCases( spec )
        elif type(spec) is list and isinstance( spec[0], TestCase):
            tcases = spec
        elif type(spec) is list:
            tcases = []
            tcasesTmp = spec[0].allTestCases()
            for idx in range( len(tcasesTmp) ):
                if idx in spec[1]:
                    tcasesTmp[idx].fName = "%s.%s:%d" % (
                            spec[0].__module__, spec[0].__name__, idx)
                    tcases.append( tcasesTmp[idx] )
        elif isinstance( spec,  basestring):
            eval(spec)
            tcases = None
        else:
            tcases = [spec]

        return tcases

if __name__ == '__main__':
    ''' Test this module here '''


