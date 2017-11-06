#! /usr/bin/env python


from kd.util.logger import getLogger
from kd.tcases.tkcd.tct_base import TctBase

logger = getLogger(__name__)

class TctPanel(TctBase):

    def __init__(self, panelId, pTypeKey='P_none', desc=None):
        if desc is None:
            desc = 'delete %s panel %d' % (pTypeKey, panelId)

        super(TctPanel, self).__init__(desc)

        self.addStep_delPanel( panelId, pTypeKey )


    def _tearDown(self, step):
        pass

    @classmethod
    def allTestCases(cls):
        return []
