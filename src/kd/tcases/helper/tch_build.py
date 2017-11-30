#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
import string

from kd.util.logger     import getLogger
from kd.util.rc_msg     import RC
from kd.util.url        import Url
from kd.tcases.tc_base  import TcBase

logger = getLogger(__name__)

class TchBuild(TcBase):

    def __init__(self, desc=None, force=False, gitTag=None, gitCommit=None,
                       gitCOSkip=False):
        if desc is None:
            desc = 'Check out and build Kodiak Container'
        super(TchBuild, self).__init__(desc)
        self.gitTag    = gitTag
        self.gitCommit = gitCommit
        self.gitRepo   = 'git@github.com:kodiakdata/KodiakContainer.git'
        self.gitCOSkip = gitCOSkip
        # add step
        if not bool(force) and not bool(gitCOSkip):
            self.addStep('Check new checkin', self._checkChg) ;
        if not bool(gitCOSkip):
            self.addStep('Check out latest code', self._checkout) ;
        self.addStep('Make and build rpm', self._build) ;

    @classmethod
    def allTestCases(cls):
        buildForce = cls.getParam( 'build.force' )
        gitTag     = cls.getParam( 'git.tag' )
        gitCommit  = cls.getParam( 'git.commit' )
        gitCOSkip  = cls.getParam( 'git.co_skip' )
        tcases = []
        tcases.append( cls(force=buildForce, gitTag=gitTag, gitCommit=gitCommit,
                           gitCOSkip=gitCOSkip) )
        return tcases

    def _prepare(self, step):
        super(TchBuild, self)._prepare(step, bHost=True)
        if not step.canContinue():
            return

        self.bHost       = self.bench.getBuildHost()
        self.gitDir      = '~/%s'               % self.bHost.url.filename
        self.gitCurr     = '~/%s.git.curr'      % self.bHost.url.filename
        self.gitLast     = '~/%s.git.last'      % self.bHost.url.filename
        self.gitLog      = '~/%s.git.log'       % self.bHost.url.filename
        self.makeOut     = '~/%s.make.out'      % self.bHost.url.filename
        self.buildRpmOut = '~/%s.build_rpm.out' % self.bHost.url.filename
        #self.bHost.run("PS1='\h \$ '")
        self.bHost.run("export TMOUT=0")
        step.setRC(RC.OK)
        return

    def _checkChg(self, step):
        while True:
            self.bHost.run("git ls-remote %s > %s" % (self.gitRepo, self.gitCurr))
            self.bHost.run("diff -q %s %s" % (self.gitCurr, self.gitLast))
            if self.bHost.getRC() == RC.OK:
                step.setRC(RC.ERROR)
                break

            step.setRC(RC.OK)
            break
        return

    def _checkout(self, step):
        self.bHost.run("rm -rf %s"   % self.gitDir)
        self.bHost.run("mkdir -p %s" % self.gitDir)
        self.bHost.run("cd %s"       % self.gitDir)
        self.bHost.run("git clone %s ." % self.gitRepo) ;
        if bool(self.gitTag):
            self.bHost.run("git checkout tags/%s" % self.gitTag)
        if bool(self.gitCommit):
            self.bHost.run("git checkout %s" % self.gitCommit)
        self.bHost.run("git log --no-color -1 > %s 2>&1;cat %s" % (self.gitLog, self.gitLog))
        msg = ""
        for line in self.bHost.getRspMsg().split('\n'):
            if line.startswith("git log") or line.startswith("cat"):
                continue
            tmp = "%s\n" % filter(lambda x: x in string.printable, line)[:-2]
            if tmp[0] == '[':
                tmp = tmp[5:]
            msg += tmp

        step.setRC(RC.OK, "Last checkin:")
        self.addNotice(step, msg, isPre=True)
        return


    def _build(self, step):
        while True:
            self.bHost.run("cd %s/tools/nanopb-0.3.3-linux-x86/generator/proto" % self.gitDir)
            self.bHost.run("make")
            self.bHost.run("cd %s" % self.gitDir)
            #self.bHost.run("./setup.sh") ;
            self.bHost.run("make OFFICIAL=1 clean") ;
            self.bHost.run("make OFFICIAL=1 > %s 2>&1" % self.makeOut) ;
            if self.bHost.run("echo $?") != RC.OK:
                step.setRC(RC.ERROR, "Failed to run make")
                break

            self.bHost.run("make build_rpm > %s 2>&1" % self.buildRpmOut) ;
            if self.bHost.run("echo $?") != RC.OK:
                step.setRC(RC.ERROR, "Failed to run make build_rpm")
                break

            self.bHost.run("/bin/grep --color=never " \
                    "'Wrote: /root/rpmbuild/RPMS/' %s" % self.buildRpmOut)
            rpmFN = self.bHost.getRslt()[0][7:]
            latest = '/root/rpmbuild/RPMS/x86_64/KodiakDataEngine_latest.rpm'
            try:
                os.unlink(latest)
            except:
                pass
            os.symlink(rpmFN, latest)

            rpmUrl = "%s://%s:%s@%s/%s" % (
                        self.bHost.url.protocol, self.bHost.url.user,
                        self.bHost.url.password, self.bHost.url.hostname, rpmFN)
            TchBuild.setParam('_rpm.url', rpmUrl)

            self.bHost.run("/bin/cp -f %s %s" % (self.gitCurr, self.gitLast))
            step.setRC(RC.OK, "RPM: %s" % rpmUrl.split('/')[-1])
            break
        return
        
if __name__ == '__main__':
    ''' Test this module here '''


