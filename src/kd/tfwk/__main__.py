#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import collections
import getopt
import sys
import os.path
from optparse import OptionParser
from kd.logging.filehandler import FileHandler
from kd.util.environ import Environ

def showTestSuite(prefix):
    from kd.tfwk.test_ctx    import TestCtx

    testCtx = TestCtx(Environ.CFG_FILE_NAME)
    testCtx.listTestSuite(prefix)

def runConfig():
    from kd.tfwk.kemail      import KEmail
    from kd.tfwk.test_case   import TestCase
    from kd.tfwk.test_set    import TestSet
    from kd.tfwk.test_folder import TestFolder
    from kd.tfwk.test_ctx    import TestCtx
    from kd.util.rc_msg      import RC
    from kd.util.logger      import getLogger
    import kd.tcases

    logger = getLogger(__name__)

    testCtx = TestCtx(Environ.CFG_FILE_NAME)
    desc, whitelist, blacklist = testCtx.loadTestCtx(Environ.TestSuit)
    TestCase.setTestCtx(testCtx)
    whitelist = eval(whitelist)
    blacklistCNs = ['kd.tcases.helper.tch_pause.TchPause'] if options.skipPause else []
    for tcase in eval(blacklist):
        fcls = tcase.__module__ + "." + tcase.__class__.__name__
        blacklistCNs.append( fcls )

    kemail = KEmail()
    if options.dryRun:
        TestCase.setParam('__force_skip__', 'enable')

    logger.info("Start %s test suite\n", desc)
    logger.debug(
        "Run %s test suite with following parameters:\n'%s'", desc, testCtx.params)
    for idx in range(len(whitelist)):
        cls = whitelist[idx]

        tcases = TestSet.genTestCasesBySpec(cls)
        if not bool(tcases):
            continue

        if type(cls) is type and not issubclass(TestFolder, cls):
            for idx in range( len(tcases)):
                tcases[idx].fName = "%s.%s:%d" % (
                        cls.__module__, cls.__name__, idx)
        for tcase in tcases:
            fcls = tcase.__module__ + "." + tcase.__class__.__name__
            if fcls in blacklistCNs:
                tcase.skip = True
                tcase.setRC(RC.OK, "Skip due to BlackList")
                continue
            tcase.run()
            kemail.addTCase( idx, tcase )
            if not tcase.canContinue():
                break
        if not tcase.canContinue():
            break

    kemail.send(options.dryRun)


parser = OptionParser()
parser.add_option("--config",     action="store",      dest="config",
                  help="test-suites configuration file")
parser.add_option("--test-suite", action="store",      dest="testSuite",
                  help="target test suite")
parser.add_option("--dry-run",    action="store_true", dest="dryRun",
                  help="Dry run")
parser.add_option("--skip-pause", action="store_true", dest="skipPause",
                  help="Skip the pause for all tests")
parser.add_option("--list",       action="store",      dest="helpList",
                  help="List matched test suites")
parser.add_option("--list-all",   action="store_true", dest="helpListAll",
                  help="List matched test suites")
parser.add_option("--no-email",   action="store_true", dest="noEmail",
                  help="do not send email notification")
parser.add_option("--wdir_tag",   action="store",      dest="wDirTag", default="",
                  help="Add extra Tag on working directory")

(options, args) = parser.parse_args()
print options
if options.config is not None:
    Environ.CFG_FILE_NAME = options.config

Environ.WDirTag  = options.wDirTag
if options.helpListAll or options.helpList is not None:
    Environ.TestSuit = "help"
    showTestSuite( options.helpList )
else:
    Environ.TestSuit = options.testSuite
    runConfig()

