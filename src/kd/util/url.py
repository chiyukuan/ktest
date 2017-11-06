#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import copy
from urlparse import urlparse
from kd.util.logger import getLogger

logger = getLogger(__name__)

class Url(object):

    def __init__(self, protocol, hostname, user, password, port=None, filename="", query=None):
        self.protocol  = protocol
        self.hostname  = hostname
        self.shostname = hostname.split(".")[0]  # short hostname
        self.user      = user
        self.password  = password
        self.port      = port
        self.filename  = filename
        self.query    = query

    @staticmethod
    def fromStr(urlStr):
        rslt = urlparse(urlStr)
        return Url(rslt.scheme, rslt.hostname, rslt.username, rslt.password, rslt.port, None if rslt.path is None else rslt.path[1:], rslt.query)


    def __str__(self):
        if self.password is None and self.user is None and self.port is None:
            return "%s://%s/%s" % (self.protocol, self.hostname, self.filename)
        if self.protocol == "scp":
            return "%s://%s@%s/%s" % (self.protocol, self.user, self.hostname, self.filename)
        if self.protocol == 'tcp':
            return "%s://%s:%d/" % (self.protocol, self.hostname, self.port)
        if self.protocol == 'http':
            return "%s://%s:%d/%s" % (self.protocol, self.hostname, self.port, self.filename)
        if self.user is not None and self.port is not None:
            return "%s://%s:%s@%s:%d/%s" % (self.protocol, self.user, self.password, self.hostname, self.port, self.filename)
        if self.port is not None:
            return "%s://%s:%d/%s" % (self.protocol, self.hostname, self.port, self.filename)
        else:
            return "%s://%s:%s@%s/%s" % (self.protocol, self.user, self.password, self.hostname, self.filename)

    def fromUrl(srcUrl, hostname=None, protocol=None, port=None, user=None, password=None, filename=None):
        url = copy.deepcopy(srcUrl)
        if hostname is not None:
            url.hostname = hostname
        if protocol is not None:
            url.protocol = protocol
        if port is not None:
            url.port = port
        if user is not None:
            url.user = user
        if password is not None:
            url.password = password
        if filename is not None:
            url.filename = filename
        return url

    def useLocalhost(self):
        self.hostname = 'localhost'
        self.password = None
        self.user     = None

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''

    url = Url.fromStr("ssh://root:kodiak@localhost:5017/")
    print url
    print url.protocol

