#! /usr/bin/env python

from kd.util.rc_msg     import RC
from kd.tcases.tc_base  import TcBase

class TchMake(TcBase):

    def __init__(self, moduleName, opt="", official=True):
        super(TchMake, self).__init__( "%smake %s with %s" % (
                "official " if bool(official) else "", moduleName, opt) )
        self.official   = official
        self.moduleName = moduleName
        self.opt        = opt

        self.addStep('make module %s' % moduleName, self._make)

    @classmethod
    def allTestCases(cls):
        return None

    def _prepare(self, step):
        super(TchMake, self)._prepare(step, bHost=True)
        if not step.canContinue():
            return

        self.bHost       = self.bench.getBuildHost()
        self.bHost.run("export TMOUT=0")
        step.setRC(RC.OK)
        return

    def _make(self, step):
        while True:
            if self.moduleName == 'kdtkcd':
                self.bHost.run("cd ~/%s/usr/src/kdtkd/kdtkcd" % (self.bHost.url.filename))
                makeCmd = "make OFFICIAL=1" if self.official else "make"

                self.bHost.run("%s clean" % makeCmd )
                self.bHost.run('%s MAKE_CFLAGS=%s' % (makeCmd, self.opt))

            break
        return
        
if __name__ == '__main__':
    ''' Test this module here '''


