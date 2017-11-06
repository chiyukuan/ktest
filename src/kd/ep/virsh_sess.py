#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import libvirt
from kd.util.logger import getLogger

logger = getLogger(__name__)

class VirshSess(object):
    ''' Short summary, should fit on one line

    Attributes:
        attr1 (str): description ...
        attr2 ....
    '''

    def __init__(self):
        self.attr1 = None
        self.attr2 = None

    def _privete(self):
        ''' private method '''
        pass

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''


