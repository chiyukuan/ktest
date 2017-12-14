#! /usr/bin/env python

from kd.util.rc_msg     import RC
from kd.tcases.tc_base  import TcBase

class TchEgrep(TcBase):

    def __init__(self, filename, params, matchCnt=None):
        if matchCnt is None:
            super(TchEgrep, self).__init__( 'egrep %s' % params )
        else:
            super(TchEgrep, self).__init__( 'egrep "%s" expect matchCnt %d' % (params, matchCnt) )
        self.filename = filename
        self.params = params
        self.matchCnt = matchCnt ;

        self.addStep('fine match pattern via egrep', self._egrep)

    @classmethod
    def allTestCases(cls):
        return None

    def _prepare(self, step):
        super(TchEgrep, self)._prepare(step, localHost=True)
        if not step.canContinue():
            return

        self.local.run("export TMOUT=0")
        step.setRC(RC.OK)
        return

    def _egrep(self, step):
        self.local.run('/bin/egrep --color=never "%s" %s' % (self.params, self.filename) )
        if self.matchCnt is None:
            step.setRC( self.local.getRC() )
        else:
            rsltCnt = 0 if self.local.getRslt() is None else len( self.local.getRslt() )

            if self.matchCnt != rsltCnt:
                step.setRC( RC.ERROR, "found %d matched pattern, but expect %d" % (
                        rsltCnt, self.matchCnt, ) )
        return
        
if __name__ == '__main__':
    ''' Test this module here '''

