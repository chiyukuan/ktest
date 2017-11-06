#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Logging plug in case to enhance existing logging scheme.

@copyright: Copyright (c) by Violin Memory, Inc. All rights reserved.
'''
import os.path
import logging
import datetime
from kd.util.environ import Environ

class WhitelistFilter(logging.Filter):

    def __init__(self, whitelist):
        self.whitelist = []
        for name in whitelist:
            self.whitelist.append( logging.Filter(name) )
            #print "add %s to white list" % (name)

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)


class BlacklistFilter(WhitelistFilter):

    def filter(self, record):
        return not WhitelistFilter.filter(self, record)

class FileHandler(logging.FileHandler):

    def __init__(self, filename, mode='a', whiteList=None, blackList=None,
                       email=False, encoding=None, delay=0):
        homeDir = os.path.expanduser('~')
        filename = filename.replace('<HOME>', homeDir)
        dtime    = datetime.datetime.now().strftime("%y%m%d_%H")
        filename = filename.replace('<TIME>', dtime)
        filename = filename.replace('<SUITE>', Environ.TestSuit)
        filename = filename.replace('<WDIR_TAG>', Environ.WDirTag)
        path = os.path.dirname(filename)
        try:
            os.makedirs(path)
        except OSError as exc:
            if not os.path.isdir(path):
                raise
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)

        if email:
            Environ.EMAIL_FILES.append( filename )
        if whiteList is not None:
            self.addFilter(WhitelistFilter( whiteList ))
        if blackList is not None:
            self.addFilter(BlacklistFilter( blackList ))

if __name__ == '__main__':
    print FileHandler('<HOME>/<TIME>/aa')
