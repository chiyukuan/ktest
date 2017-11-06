#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

Logging plug in case to enhance existing logging scheme.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import logging

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


class StreamHandler(logging.StreamHandler):

    def __init__(self, whiteList=None, blackList=None, stream=None):

        logging.StreamHandler.__init__(self, stream=stream)
        if whiteList is not None:
            self.addFilter(WhitelistFilter( whiteList ))
        if blackList is not None:
            self.addFilter(BlacklistFilter( blackList ))

if __name__ == '__main__':
    ''' Test this module here '''


