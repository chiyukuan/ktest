#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.tfwk.test_case import TestCase
from kd.tfwk.test_set import TestSet
import kd.tcases

logger = getLogger(__name__)

class TcsSimple(TestSet):
    '''
    TestSet simle use the testSetName to find the testSpecs from ktest.ini file
    '''

    def __init__(self, testSetName, desc=None):
        tcSet = eval( TestCase.getParam( 'test_set.' + testSetName ) )
        print tcSet
        if desc is None:
            super(TcsSimple, self).__init__(tcSet[0])
        else:
            super(TcsSimple, self).__init__(desc)

        self.tcsSpecs = tcSet[1]

    def _getTestSpecs(self):
        return self.tcsSpecs


