#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import os
import shutil
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.util.url import Url
from kd.tfwk.test_case import TestCase
from kd.ep.ep_ctx import getTkcdCtx
from kd.tcases.tc_helper import TcHelper

logger = getLogger(__name__)

class TchReset(TestCase):

    def __init__(self, desc, dockName, nodeList, tkcdUrl):
        super(TchReset, self).__init__(None, desc)
        self.dockName = dockName
        self.nodeList = nodeList
        self.tkcdUrl  = tkcdUrl

        self.addStep("Delete tmp device mount dir",    self._delMDirs)
        self.addStep("Delete Persistent Runtime data", self._delPersistData)
        self.addStep("Delete Data files",              self._delDFiles)

    @classmethod
    def allTestCases(cls):
        tkcdUrl  = cls.getParamUrl('tkcd.url')
        dockName = cls.getParam('dock.name')
        nodeList = cls.getParamEval('node.list')
        tcases = []
        tcases.append( cls( "Reset All", dockName, nodeList, tkcdUrl ) )
        return tcases

    def _prepare(self, step):
        step.setRC(RC.OK)
        return

    def _tearDown(self, step):
        step.setRC(RC.OK)
        return

    def _delMDirs(self, step):
        mpath = "/tmp/kodiak/dock"
        if os.path.exists( mpath ):
            shutil.rmtree( mpath )
        step.setRC(RC.OK)
        return


    def _delPersistData(self, step):
        for node in self.nodeList:
            cfgDirRoot = "/kodiak/dock/%s/docknode/%d/cfg" % (self.dockName, node)
            for dItem in [ "/poolkeeper", "/tilekeeper" ]:
                cfgDir = "%s/%s" % (cfgDirRoot, dItem)
                if os.path.exists( cfgDir ):
                    shutil.rmtree( cfgDir )
        step.setRC(RC.OK)
        return

    def _delDFiles(self, step):
        for node in self.nodeList:
            mntDirRoot = "/kodiak/dock/%s/docknode/%d/mnt" % (self.dockName, node)
            for mIdx in range(256):
                mntDir = "%s/%d" % (mntDirRoot, mIdx)
                if not os.path.exists( mntDir ):
                    continue

                # mnt directory exist
                for fName in os.listdir(mntDir):
                    if (fName == '.' or fName == '..'):
                        continue
                    fPath = os.path.join(mntDir, fName)
                    try:
                        if os.path.isfile( fPath ):
                            os.unlink( fPath )
                        elif os.path.isdir( fPath ):
                            shutil.rmtree( fPath )
                    except Exception as e:
                        logger.exception(e)
        step.setRC(RC.OK)
        return

if __name__ == '__main__':
    ''' Test this module here '''


