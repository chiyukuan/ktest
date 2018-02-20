#! /usr/bin/env python


from kd.util.logger import getLogger
from kd.tcases.tkcd.tct_base import TctBase

logger = getLogger(__name__)

class TctSshot( TctBase ):

    def __init__(self, cmd='add', readonly=True, panelIds=[]):
        self.cmd = cmd.lower()
        self.readonly = readonly
        self.panelIds = panelIds
        if self.cmd == 'add':
            super(TctSshot, self).__init__('Add %s snapshot panels:%s' % (
                "ReadOnly" if self.readonly else "ReadWrite",
                self.panelIds))
            self.addStep_addSnapshot(readonly, panelIds)

        else:
            super(TctSshot, self).__init__('Del %s snapshot panels:%s' % (
                "ReadOnly" if self.readonly else "ReadWrite",
                self.panelIds))

    def _privete(self):
        ''' private method '''
        pass

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


