#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import os.path

class Environ(object):

    ROOT_DIR      = '%s/.ktest' % os.path.expanduser('~')
    CFG_FILE_NAME = '%s/%s' % (ROOT_DIR, 'ktest.ini')
    EMAIL_FILES   = []
    TestSuit      = "unknown"
    WDirTag       = ""

    def __init__(self):
        pass


