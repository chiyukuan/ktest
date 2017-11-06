#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import os.path
import logging.config

from environ import Environ

# _ variable
_LoggerInit = False

# 2 empty lines between top-level funcs and classes


def getLogger(name):
    global _LoggerInit
    if not _LoggerInit:
        if os.path.isfile(Environ.CFG_FILE_NAME):
            logging.config.fileConfig(Environ.CFG_FILE_NAME)
        else:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(levelname)s %(message)s')
        _LoggerInit = True
    return logging.getLogger(name)


if __name__ == '__main__':

    logger = getLogger('MyLogger1')
    logger.info("INFO message1")

    logger2 = getLogger('MyLogger2')
    logger2.info("INFO message2")
