#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import os
import sys
from kd.util.logger import getLogger
logger = getLogger(__name__)

class Package(object):
    ''' Default package handler when someone load this package '''

    attrs = dict()

    def __init__(self, cls):
        if cls.__module__ not in cls.attrs:
            cls.attrs[cls.__module__] = ([], [], []) # packages, files, tcases

            dirname = os.path.dirname(sys.modules[cls.__module__].__file__)
            for module in os.listdir(dirname):

                if os.path.isdir(dirname + "/" + module):
                    # package
                    cls.attrs[cls.__module__][0].append(module)
                elif module == '__init__.py' or module[-3:] != '.py':
                    continue
                else:
                    # .py file
                    module = module[:-3]
                    cls.attrs[cls.__module__][1].append(module)

                fmodule = module if cls.__module__ == '__main__' else cls.__module__ + \
                    "." + module

                __import__(fmodule, locals(), globals())

            del module



