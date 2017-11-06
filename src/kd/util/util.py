#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

def must_override(f):
    def t(*args):
        raise NotImplementedError("You must override %s" % (f.__name__))
    return t


def not_supported(f):
    def t(*args):
        raise NotImplementedError("%s is not supported any more." % f.__name__)

