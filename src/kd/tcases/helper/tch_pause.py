#! /usr/bin/env python

from kd.tfwk.test_case import TestCase

class TchPause(TestCase):

    def __init__(self, cmd, params=None):
        if 'enter_and_continue' == cmd:
            super(TchPause, self).__init__(None, 'Enter and continue')
            self.addStep("Press", self._enterContinue, opq=[False, params])
        if 'yes_to_continue' == cmd:
            super(TchPause, self).__init__(None, 'Enter and continue')
            self.addStep("Press", self._enterContinue, opq=[True, params])

    @classmethod
    def allTestCases(cls):
        return None

    def _prepare(self, step):
        return

    def _tearDown(self, step):
        return

    def _enterContinue(self, step):
        needPermit, msg = step.opq
        while True:
            if msg is None:  break

            print ""
            if isinstance(msg, basestring):
                print msg
                break

            if isinstance(msg, (list, tuple)):
                for item in msg:
                    if isinstance(item, (list, tuple)):
                        for subItem in item:
                            print "  - %s" % item
                    else:
                        print "- %s" % item 
                break

            if isinstance(msg, dict):
                for key, items in msg.iteritems():
                    print "- %s" % key
                    for item in items:
                        if isinstance(item, dict):
                            for subKey, subItems in item.iteritems():
                                print "  - %s" % subKey
                                for subItem in subItems:
                                    print "    - %s" % subItem
                        else:
                            print "  - %s" % item
            break

        if needPermit:
            yesno=raw_input("\ncontinue (yes/no)?").upper()
            if "YES" == yesno or "Y" == yesno:
                pass
            else:
                self.forceSkipAll( step )
        else:
            raw_input("\nPress Enter to continue ...")

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

