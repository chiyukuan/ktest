#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import logging
from kd.util.logger import getLogger
from kd.util.util   import must_override
from kd.util.rc_msg   import RC
from kd.util.url   import Url
from kd.tfwk.runnable import Runnable

logger = getLogger(__name__)

class TestCaseNotice(object):
    def __init__(self, level, desc, isPre=False, listItem=True):
        self.level = level
        self.desc  = desc
        self.isPre = isPre
        self.listItem = listItem

    def __str__(self):
        return self.desc

    __repr__ = __str__

class TestCase(Runnable):
    ''' Base test case class. It defines the basic behavior of a testcase '''

    testCtx = None

    def __init__(self, tcaseId, desc):
        super(TestCase, self).__init__(tcaseId, desc, None)
        self.rIdx       = 0
        self.steps      = []
        self.params     = dict()
        self.notices    = []
        self.stepNotices= []
        self.hasWarning = False
        self.critical   = True      # is a critical test case

    def needNotify(self):
        return self.hasWarning or self.critical

    def addStep(self, desc, method, opq=None):
        step = Runnable( self.nextTag(len(self.steps)), desc, method, opq )
        self.steps.append(step)

    @must_override
    def _prepare(self, tstep):
        pass

    @must_override
    def _teardown(self, tstep):
        pass

    def _onError(self, tstep):
        pass

    def _getSteps(self):
        prepareStep  = Runnable( self.nextTag( -1 ),
                                 "Prepare testcase", self._prepare)
        tearDownStep = Runnable( self.nextTag(len(self.steps)),
                                 "Teardown testcase", self._tearDown)
        return [prepareStep] + self.steps + [tearDownStep]

    def run(self):
        logger.info("--")
        logger.info("-- Start '%s'", self.desc)
        logger.info("--")

        # execute this test case
        self._start()
        # run test steps
        steps = self._getSteps()
        for step in steps:
            if self.needSkip():
                step.setRC(RC.WARNING, "Force skip")
                if self.skip:
                    break
            else:
                try:
                    step.run()
                except Exception as e:
                    step.setRC(RC.ERROR,
                               "Catch unhandled exception. Fix python code is required")
                    logger.exception(e)
            self.rIdx += 1
            if step.rcMsg.rc == RC.WARNING:
                self.hasWarning = True

            if not step.canContinue():
                self._onError(step)
                self.notices.append( TestCaseNotice(logging.ERROR,
                            "%s '%s': [%s]" % (step.tag, step.desc, step.rcMsg)))
                break
            else:
                if bool(step.rcMsg.msg):
                    if step.rcMsg.rc == RC.OK:
                        self.notices.append( TestCaseNotice(logging.INFO,
                            "%s '%s': %s" % (step.tag, step.desc, step.rcMsg.msg)) )
                    else:
                        self.notices.append( TestCaseNotice(logging.WARNING,
                            "%s '%s': [%s]" % (step.tag, step.desc, step.rcMsg)) )

            if bool(self.stepNotices):
                for stepNotice in self.stepNotices:
                    self.notices.append( stepNotice )
                self.stepNotices = []

        self.rcMsg = step.rcMsg
        self._end()

        if self.hasParam('__force_teardown__'):
            teardownStep = steps[-1]
            if teardownStep.rcMsg.rc == RC.NOT_YET:
                logger.info(
                    "Testcase failed and start the teardown step always")
                teardownStep.run()

        if self.canContinue():
            if self.hasWarning:
                self.rcMsg.rc = RC.WARNING
            logger.info("   Result: %s in %s",
                        self.rcMsg, self.timeDuration())
        else:
            logger.error("   Result: %s at %d/%d steps in %s",
                         self.rcMsg, self.rIdx, len(self.steps) + 2, self.timeDuration())
        if bool(self.notices):
            logger.info("   Notes:")
        for notice in self.notices:
            if isinstance(notice, TestCaseNotice):
                logger.info("    - %s", notice.desc)
            else:
                logger.info("    - %s", notice)
        logger.info("")

        return self.rcMsg.rc

    def addNotice(self, step, msg, level=logging.INFO, isPre=False, listItem=True):
        if isPre or not listItem:
            self.stepNotices.append( TestCaseNotice(level, msg, isPre, listItem) )
        else:
            self.stepNotices.append( TestCaseNotice(level,
                             "%s '%s': %s" % (step.tag, step.desc, msg)) )

    @classmethod
    def isForceSkip(cls): return cls.checkParam('__force_skip__', 'enable')

    def needSkip(self): return self.skip or TestCase.isForceSkip()

    def forceSkipAll(self, tStep):
        if not TestCase.checkParam('__force_skip__', 'enable'):
            TestCase.setParam('__force_skip__', 'enable')
            if tStep.rcMsg.msg is None:
                tStep.rcMsg.msg = " And force to skip remaining test case"
            else:
                tStep.rcMsg.msg += " And force to skip remaining test case"

    @classmethod
    def allTestCases(cls):
        return None

    @classmethod
    def setTestCtx(cls, testCtx):
        cls.testCtx = testCtx

    @classmethod
    def getParam(cls, name):
        return cls.testCtx.getParam(name.lower())

    @classmethod
    def setParam(cls, name, value): cls.testCtx.setParam(name.lower(), value)

    @classmethod
    def setBench(cls, benchName):
        cls.setParam('_bench', cls.getParam(benchName))

    @classmethod
    def resetBench(cls):
        cls.testCtx.popParam('_bench')

    @classmethod
    def checkParam(cls, name, value): return cls.testCtx.checkParam(name.lower(), value)

    @classmethod
    def hasParam(cls, name): return cls.testCtx.hasParam(name.lower())

    @classmethod
    def needEmail(cls): return cls.checkParam('email', 'enable')

    @classmethod
    def setTestFolder(cls, tFolder): cls.setParam('__testFolder__', tFolder)

    @classmethod
    def unsetTestFolder(cls): cls.testCtx.params.pop('__testFolder__', None)

    @classmethod
    def getTestFolder(cls): return cls.getParam('__testFolder__')

    @classmethod
    def getParamUrl(cls, name):
        urlStr = cls.getParam(name)
        return Url.fromStr( urlStr ) if bool(urlStr) else None

    @classmethod
    def getParamEval(cls, name):
        sValue = cls.getParam(name)
        return eval( sValue ) if isinstance( sValue, basestring ) else sValue

    @classmethod
    def getParamExactEval(cls, name):
        sValue = cls.testCtx.getParamExact(name.lower())
        return None if sValue is None else eval( sValue )

    @classmethod
    def getWorkDir(cls):
        if cls.hasParam('work_dir'):
            return cls.getParam('work_dir')
        else:
            return cls.getParam('default_work_dir')

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


