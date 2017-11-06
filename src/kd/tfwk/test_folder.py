#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger
from kd.util.package import Package
from kd.tfwk.test_case import TestCase

logger = getLogger(__name__)

class TestFolder(Package, TestCase):
    '''
    test folder group all test cases under the same folder.
    '''
    def __init__(self, package, stepId=None, desc=None):
        Package.__init__(self, package)
        TestCase.__init__(self, stepId, desc)

        #logger.debug("package %s module %s", package, package.__module__)
        if package.__module__ == 'kd.tcases':
            classes = TestCase.__subclasses__()

            for cls in classes:
                myPackage = cls.__module__[:cls.__module__.rfind('.')]
                if myPackage in package.attrs:
                    package.attrs[myPackage][2].append( cls )
                classes2 = cls.__subclasses__()
                if classes2:
                     classes.extend(classes2)

    def _prepare(self, tStep):
        pass

    def _tearDown(self, tStep):
        pass

    @classmethod
    def allTestCases(cls):
        cls.setTestFolder(cls.__module__)
        tcases = []
        # logger.debug("package %s class %s", cls.__module__, TestFolder.attrs[cls.__module__])
        for cls in TestFolder.attrs[cls.__module__][2]:
            #logger.debug("extend testcases from %s class", cls)
            tcases.extend( cls.allTestCases( ) )
        for idx in range( len(tcases)):
            tcases[idx].fName = "%s.All:%d" % (cls.__module__, idx)
        cls.unsetTestFolder()
        return tcases

