#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

from kd.util.logger import getLogger

logger = getLogger(__name__)

class IometerIcf(object):

    # runSpec: [txSize, read percentage, random percentage]
    def __init__(self, runTime, runSpec, osio=8, workerPerTarget=1):
        self.runHour = runTime[0]
        self.runMin  = runTime[1]
        self.runSec  = runTime[2]
        # size, % of size,% reads,% random,delay,burst,align,reply
        self.aSpec     = [runSpec[0], 100, runSpec[1], runSpec[2], 0, 1, 0, 0] 
        self.aSpecName = '%d KiB; %d%% Read; %d%% random' % (
                    self.aSpec[0]/1024, self.aSpec[2], self.aSpec[3])
        self.osio    = osio
        self.workerPerTarget = workerPerTarget

    def setTxSz(self, txSz):
        self.aSpec[0]  = txSz
        self.aSpecName = '%d KiB; %d%% Read; %d%% random' % (
                    self.aSpec[0]/1024, self.aSpec[2], self.aSpec[3])

    def __writeTestSetup(self):
        # {{{
        self.fd.write( """'TEST SETUP ====================================================================
'Test Description
	
'Run Time
'	hours      minutes    seconds
	%d          %d          %d
'Ramp Up Time (s)
	0
'Default Disk Workers to Spawn
	NUMBER_OF_CPUS
'Default Network Workers to Spawn
	0
'Record Results
	ALL
'Worker Cycling
'	start      step       step type
	1          1          LINEAR
'Disk Cycling
'	start      step       step type
	1          1          LINEAR
'Queue Depth Cycling
'	start      end        step       step type
	1          32         2          EXPONENTIAL
'Test Type
	NORMAL
'END test setup
""" % (self.runHour, self.runMin, self.runSec))
        # }}}

    def __writeResultDisplay(self):
        # {{{
        self.fd.write( """'RESULTS DISPLAY ===============================================================
'Record Last Update Results,Update Frequency,Update Type
	DISABLED,1,LAST_UPDATE
'Bar chart 1 statistic
	Total I/Os per Second
'Bar chart 2 statistic
	Total MBs per Second (Decimal)
'Bar chart 3 statistic
	Average I/O Response Time (ms)
'Bar chart 4 statistic
	Maximum I/O Response Time (ms)
'Bar chart 5 statistic
	% CPU Utilization (total)
'Bar chart 6 statistic
	Total Error Count
'END results display
""")
        # }}}

    def __writeAccessSpec(self):
        # {{{
        self.fd.write( """'ACCESS SPECIFICATIONS =========================================================
'Access specification name,default assignment
	%s,NONE
'size,%% of size,%% reads,%% random,delay,burst,align,reply
	%d,%d,%d,%d,%d,%d,%d,%d
'END access specifications
""" % (self.aSpecName,
            self.aSpec[0], self.aSpec[1], self.aSpec[2], self.aSpec[3],
            self.aSpec[4], self.aSpec[5], self.aSpec[6], self.aSpec[7]))
        # }}}

    def __writeWorker(self, workerId, target, diskMax=0, sSector=0):
        # {{{
        #diskMax = 83886080 if target.endswith(" [xfs]") else 0
        self.fd.write( """'Worker
	Worker %d
'Worker type
	DISK
'Default target settings for worker
'Number of outstanding IOs,test connection rate,transactions per connection,use fixed seed,fixed seed value
	%d,DISABLED,1,DISABLED,0
'Disk maximum size,starting sector,Data pattern
	%d,%d,0
'End default target settings for worker
'Assigned access specs
        %s
'End assigned access specs
'Target assignments
'Target
	%s
'Target type
	DISK
'End target
'End target assignments
'End worker
""" % (workerId, self.osio, diskMax, sSector, self.aSpecName, target))
        # }}}

    def __writeManagerList(self, managers):
        # {{{
        managerId = 1
        workerId  = 1
        self.fd.write( "'MANAGER LIST ==================================================================\n" )
        for manager in managers:
            self.fd.write( """'Manager ID, manager name
	%d,%s
'Manager network address
	%s
""" % (managerId, manager[0], manager[1]))

            for target in manager[2]:
                if isinstance(target, basestring):
                    self.__writeWorker(workerId, target)
                    workerId += 1
                else:
                    segSz = target[1] / (512 * self.workerPerTarget)
                    sSectors = range(0, target[1] / 512, segSz)
                    for idx in range(len(sSectors)):
                        self.__writeWorker(workerId, target[0],
                                sSectors[idx] + segSz, sSectors[idx])
                        workerId += 1

            self.fd.write("'End manager\n")
            managerId += 1

        self.fd.write("'END manager list\n")
        # }}}

    def write(self, filename, managers):
        self.fd = open(filename, 'w')
        self.fd.write("Version 1.1.0\n")
        self.__writeTestSetup()
        self.__writeResultDisplay()
        self.__writeAccessSpec()
        self.__writeManagerList(managers)
        self.fd.write("Version 1.1.0\n")
        self.fd.close()

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

if __name__ == '__main__':
    ''' Test this module here '''
    icf = IometerIcf([0,1,30], [256 * 1024, 0, 100], 16)
    icf.write('test.icf', [['kd-cube2-win',         '192.168.1.19', []],
                           ['kodiak-cube2-c71-vm3', '192.168.1.13', 
                               ['/kodiak/dock/c10a8e28-bf79-421b-96b9-55e43c098c0a/docknode/1/mnt/0 [xfs]',
                                '/kodiak/dock/c10a8e28-bf79-421b-96b9-55e43c098c0a/docknode/2/mnt/0 [xfs]']]])


