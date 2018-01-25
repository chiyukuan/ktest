#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''

import time
import random
from kd.util.logger import getLogger
from kd.util.rc_msg import RC
from kd.tfwk.test_case import TestCase
from kd.util.url import Url
from kd.util.kspawn import execUrlSess
from kd.text.kd_res import KdRes
from kd.tcases.tc_bench import TcBench
from kd.tcases.tc_base import TcBase
from kd.tcases.tc_helper import TcHelper

logger = getLogger(__name__)

class TchDhost(TcBase):

    def __init__(self, cmd, params=None, desc=None):
        cmd = cmd.lower()
        if 'stop' == cmd:
            if params is None:
                super(TchDhost, self).__init__('Stop the Kodiak Apps')
            else:
                super(TchDhost, self).__init__('Stop the Kodiak Apps for node %s' % params)

            self.addStep("Stop kodiak apps",  self._stopAll, opq=params)
            self.addStep("Check kodiak apps", self._stopCheck, opq=params)

        elif 'restart' == cmd:
            if params is None:
                super(TchDhost, self).__init__('Restart the Kodiak Apps')
            else:
                super(TchDhost, self).__init__('Restart the Kodiak Apps for node %s' % params)
            self.addStep("Stop kodiak apps",  self._stopAll, opq=params )
            self.addStep("Check kodiak apps", self._stopCheck, opq=params)

            self.addStep("Start kodiak apps", self._startAll, opq=params)
            self.addStep("Check kodiak apps", self._startCheck, opq=params)

        elif 'reset' == cmd:
            super(TchDhost, self).__init__('reset dock configuration')
            self.addStep("Stop kodiak apps",  self._stopAll )
            self.addStep("Check kodiak apps", self._stopCheck)
            self.addStep("reset dock", self._reset, opq=[True,False])

        elif 'reset_all' == cmd:
            super(TchDhost, self).__init__('reset all configuration')
            self.addStep("Stop kodiak apps",  self._stopAll )
            self.addStep("Check kodiak apps", self._stopCheck)
            self.addStep("reset all", self._reset, opq=[True,True])

        elif 'reset_data' == cmd:
            super(TchDhost, self).__init__('reset data')
            self.addStep("Stop kodiak apps",  self._stopAll )
            self.addStep("Check kodiak apps", self._stopCheck)
            self.addStep("reset data", self._reset, opq=[False,False])

        elif 'reset_tkcd' == cmd:
            super(TchDhost, self).__init__('reset tkcd database')
            self.addStep("reset TKCD database",  self._resetTkcd, opq=params )

        elif 'backup_tkcd' == cmd:
            super(TchDhost, self).__init__('backup tkcd database')
            self.addStep("backup TKCD database",  self._backupTkcd )

        elif 'restore_tkcd' == cmd:
            super(TchDhost, self).__init__('restore tkcd database')
            self.addStep("restore TKCD database",  self._restoreTkcd )

        elif 'init' == cmd:
            super(TchDhost, self).__init__('initial setup configuration')
            self.addStep("Stop kodiak apps",  self._stopAll )
            self.addStep("Check kodiak apps", self._stopCheck)
            self.addStep("initialize configuration", self._initAll)

        elif 'insmod' == cmd:
            super(TchDhost, self).__init__('insert kodiak driver')
            self.addStep("Stop kodiak apps",  self._insmod )

        elif 'format-xfs' == cmd or 'rdisk-format-xfs' == cmd:
            if params is None:
                params = '-b size=4096 -s size=4096'
            super(TchDhost, self).__init__('format data disk with param, %s' % params)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep('format data disk', self._rdiskFormat, opq=params )

        elif 'nvme-format-xfs' == cmd:
            if params is None:
                params = '-b size=4096 -s size=4096'
            super(TchDhost, self).__init__('format data disk with param, %s' % params)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
            self.addStep('format data disk', self._rdiskFormat, opq=params )

        elif 'nvme-format-ext4' == cmd:
            if params is None:
                params = '-b 4096'
            super(TchDhost, self).__init__('ext4 format data disk with param, %s' % params)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
            self.addStep('format data disk', self._rdiskFormatExt4, opq=params )

        elif 'vdisk-format-xfs' == cmd:
            if params is None:
                params = '-b size=4096 -s size=4096'
            super(TchDhost, self).__init__('format vdisk with param, %s' % params)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
            self.addStep('format data disk', self._vdiskFormat, opq=params )

        elif 'mount' == cmd or 'rdisk-mount-xfs' == cmd:
            super(TchDhost, self).__init__('mount data disk')
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep("mount kodiak data disk",  self._rdiskMount, opq=params )

        elif 'nvme-mount' == cmd:
            super(TchDhost, self).__init__('mount vdisk')
            self.addStep_getDeviceList( TcBase.DEV_TYPE.NVME )
            self.addStep("mount vdisk",  self._rdiskMount, opq=params )

        elif 'vdisk-mount-xfs' == cmd:
            super(TchDhost, self).__init__('mount vdisk')
            self.addStep_getDeviceList( TcBase.DEV_TYPE.VDISK )
            self.addStep("mount vdisk",  self._vdiskMount, opq=params )

        elif 'umount' == cmd:
            super(TchDhost, self).__init__('umount kodiak data disk')
            self.addStep("umount kodiak data disk",  self._umount, opq=params )

        elif 'rdisk-umount' == cmd:
            super(TchDhost, self).__init__('umount raw data disk')
            self.addStep("umount kodiak data disk",  self._vdiskUMount, opq=params )

        elif 'vdisk-umount' == cmd:
            super(TchDhost, self).__init__('umount kodiak vdisk')
            self.addStep("umount kodiak data disk",  self._vdiskUMount, opq=params )

        elif 'rdisk-del' == cmd:
            super(TchDhost, self).__init__('delete physical device')
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            if params is None:
                self.addStep("del the all  physical device", self._rdiskDel)
            else:
                self.addStep("del the physical device %d" % params, self._rdiskDel, opq=params )

        elif 'rdisk-rand-del' == cmd:
            super(TchDhost, self).__init__('random delete one physical device')
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep("random del one physical device", self._rdiskRandDel)

        elif 'rdisk-rescan' == cmd:
            super(TchDhost, self).__init__('rescan all physical device')
            self.addStep("rescan all physical device", self._rdiskRescan )

        elif 'rdisk-max' == cmd:
            super(TchDhost, self).__init__('limit available physical device count to %d' % params)
            self.addStep("rescan all physical device", self._rdiskRescan )
            self.addStep("limit %d physical devices" % params, self._rdiskMax, opq=params )

        elif 'set-io-scheduler' == cmd:
            super(TchDhost, self).__init__('set IO scheduler to %s' %
                    "cfq" if params is None else params)
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep("set IO scheduler for all available data disks",
                         self._setIoScheduler, opq=params )

        elif 'secure-erase' == cmd:
            super(TchDhost, self).__init__('Secure Erase SSD')
            self.addStep_getDeviceList( TcBase.DEV_TYPE.RAW )
            self.addStep("Secure Erase SSDs", self._secureErase, opq=params )

        elif 'rebuild-status' == cmd:
            super(TchDhost, self).__init__('get rebuild result' if desc is None else desc)
            self.addStep("get rebuild result", self._rbdStatus )

        elif 'start' == cmd:
            if params is None:
                super(TchDhost, self).__init__('Start the Kodiak Apps')
            else:
                super(TchDhost, self).__init__('Start the Kodiak Apps for node %s' % params)

            self.addStep("Start kodiak apps", self._startAll, opq=params)
            self.addStep("Check kodiak apps", self._startCheck, opq=params)

        elif 'hello' == cmd:
            super(TchDhost, self).__init__('Hello each host')
            self.addStep("Echo hello", self._hello)

    @classmethod
    def allTestCases(cls):
        return None

    def _prepare(self, step):
        super(TchDhost, self)._prepare(step, appHost=True, dockHost=True, localHost=True)
        if not step.canContinue():
            return

        self.npmOpt = TestCase.getParam( 'npm.opt' )

    def _rmmod(self, step):
        wlist = step.opq
        idx   = -1
        for host in self.bench.getAppHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('pkill -9 node')
            host.run('/usr/sbin/lsmod | /bin/grep --color=never kodiak')
            while host.getRslt() is not None:
                # check reference count
                if host.getRslt()[1] == 0:
                    host.run('rmmod kodiak > /dev/null 2>&1')
                    host.run('echo $?')
                    if host.getRC() != RC.OK:
                        step.setRC(RC.ERROR, 'Failed to remove mod kodiak %s' % host) ;
                    return
                # sleep
                print "kodiak reference count is not 0. sleep 10 and try again"
                time.sleep(10)
                host.run('/usr/sbin/lsmod | /bin/grep --color=never kodiak')

    def _startAll(self, step):
        wlist = step.opq
        idx   = -1

        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue
            host.run('/bin/systemctl is-active kodiak-data-engine')
            if host.getRslt():
                host.run('/bin/systemctl stop kodiak-data-engine')
            host.run('/usr/sbin/logrotate --force /etc/logrotate.d/kodiak')

        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('/bin/logger -p local5.notice "=="')
            host.run('/bin/logger -p local5.notice "== Starting Kodiak Software on \"`date`\""')
            host.run('/bin/logger -p local5.notice "=="')
            if self.npmOpt is not None:
                host.run('systemctl set-environment %s' % self.npmOpt)

            host.run('%s /bin/systemctl start kodiak-data-engine' % ("" if self.npmOpt is None else self.npmOpt))


        '''
        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('pkill -9 node')
            host.run('pkill -9 kdtkcd')
            host.run('mkdir -p /dev/kodiak')

            host.run('/bin/ls %s' % self.bench.resourceCfg)
            if bool(host.getRslt()):

                resFN = '%s/auto_%s_resources.cfg' % (TcBase.getWorkDir(), host)
                url = Url.fromUrl(host.url, protocol='scp', filename=self.bench.resourceCfg)
                execUrlSess( url, scpTo=resFN)
                res = KdRes( resFN )

                for disk in res.getSsds():
                    device = disk['device']
                    host.run('/bin/umount %s > /dev/null 2>&1' % device)
                    host.run('/bin/ln -sf /dev/%s %s' % (device[21:], device))

            host.run('echo 4 > /proc/sys/kernel/printk')
            host.run('/usr/sbin/logrotate --force /etc/logrotate.d/kodiak')

        self._rmmod(step)
        if not step.canContinue():
            return

        idx   = -1
        for host in self.bench.getAppHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('echo 4 > /proc/sys/kernel/printk')

            host.run('insmod /opt/Kodiak/kmodules/kodiak.ko > /dev/null 2>&1')
            host.run('echo $?')
            if host.getRC() != RC.OK:
                step.setRC(RC.ERROR, 'Failed to install mod kodiak at %s' % host) ;
                return

            host.run('/bin/echo "" > %s' % self.bench.debugLog)

            host.run('cd /opt/Kodiak/nodejs/dockport')
            host.run('echo "--" | tee -a %s' % self.bench.debugLog)
            host.run('echo "-- Starting Kodiak NoMAD on \"`date`\"" | tee -a %s' % self.bench.debugLog)
            host.run('echo "--" | tee -a %s' % self.bench.debugLog)
            host.run('(nohup npm start dockport >> %s 2>&1 &) > /dev/null 2>&1' % self.bench.debugLog)


        idx   = -1
        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('cd /opt/Kodiak/nodejs/kdhmgr')
            host.run('/bin/logger -p local5.notice "=="')
            host.run('/bin/logger -p local5.notice "== Starting Kodiak Software on \"`date`\""')
            host.run('/bin/logger -p local5.notice "=="')
            host.run('%s npm start kdhmgr &' % ("" if self.npmOpt is None else self.npmOpt))
            print    '%s npm start kdhmgr &' % ("" if self.npmOpt is None else self.npmOpt)

        '''

        return

    def _insmod(self, step):
        self._rmmod(step)
        if not step.canContinue():
            return

        for host in self.bench.getAppHosts():
            host.run('echo 4 > /proc/sys/kernel/printk')

            host.run('insmod /opt/Kodiak/kmodules/kodiak.ko > /dev/null 2>&1')
            host.run('echo $?')
            if host.getRC() != RC.OK:
                step.setRC(RC.ERROR, 'Failed to install mod kodiak at %s' % host) ;
                return

    def _rdiskFormat(self, step):
        params = step.opq
        for host in self.bench.getDockHosts():
            for dev in host.devs:
                host.run( "mkfs.xfs %s -f %s" % (params, dev.devName) )
                time.sleep(10)

    def _rdiskFormatExt4(self, step):
        params = step.opq
        for host in self.bench.getDockHosts():
            for dev in host.devs:
                host.run( "mkfs.ext4 %s %s" % (params, dev.devName) )

    def _vdiskFormat(self, step):
        params = step.opq
        for host in self.bench.getAppHosts():
            for dev in host.devs:
                host.run( "mkfs.xfs %s -f %s" % (params, dev.devName) )
                #print "mkfs.xfs %s -f %s" % (params, dev.devName)

    def _rdiskMount(self, step):
        for host in  self.bench.getDockHosts():
            for devIdx in range(len(host.devs)):
                mdir = "/kodiak/dock/%s/docknode/1/mnt/%d" % (self.bench.getDockName(), devIdx )
                host.run("mkdir -p %s" % mdir)
                #host.run("mount -t xfs %s %s" % ( host.devs[devIdx].devName, mdir ))
                host.run("mount %s %s" % ( host.devs[devIdx].devName, mdir ))
                #print "mount -t xfs %s %s" % ( host.devs[devIdx].devName, mdir )


    def _vdiskMount(self, step):
        for host in  self.bench.getAppHosts():
            for devIdx in range(len(host.devs)):
                mdir = "/kodiak/dock/%s/appnode/1/mnt/%d" % (self.bench.getDockName(), devIdx )
                host.run("mkdir -p %s" % mdir)
                host.run("mount -t xfs %s %s" % ( host.devs[devIdx].devName, mdir ))

    def _vdiskUMount(self, step):
        if step.opq is not None:
            for host in self.bench.getDockHosts():
                host.run('/bin/umount %s' % step.opq)
                host.run('/bin/rm -rf %s' % step.opq)
            return

        for host in self.bench.getAppHosts():
            host.run('/bin/umount /kodiak/dock/%s/appnode/*/mnt/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/appnode/*/mnt/*' % self.bench.getDockName())

    def _rdiskUMount(self, step):
        if step.opq is not None:
            for host in self.bench.getDockHosts():
                host.run('/bin/umount %s' % step.opq)
                host.run('/bin/rm -rf %s' % step.opq)
            return

        for host in self.bench.getDockHosts():
            host.run('/bin/umount /kodiak/dock/%s/docknode/*/mnt/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/mnt/*' % self.bench.getDockName())

    def _umount(self, step):
        if step.opq is not None:
            for host in self.bench.getDockHosts():
                host.run('/bin/umount %s' % step.opq)
                host.run('/bin/rm -rf %s' % step.opq)
            return

        for host in self.bench.getDockHosts():
            host.run('/bin/umount /kodiak/dock/%s/docknode/*/mnt/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/mnt/*' % self.bench.getDockName())

        for host in self.bench.getAppHosts():
            host.run('/bin/umount /kodiak/dock/%s/appnode/*/mnt/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/appnode/*/mnt/*' % self.bench.getDockName())

    def _rdiskDel(self, step):
        delIdx = step.opq

        # delete all pDisk
        if delIdx is None:
            for host in self.bench.getDockHosts():
                for dev in host.devs:
                    host.run("echo 1 > /sys/bus/scsi/devices/%s/delete" % dev.scsiAddr)
            return

        # delete few pDisk
        for host in self.bench.getDockHosts():
            if len(host.devs) <= delIdx:
                continue

            host.run("echo 1 > /sys/bus/scsi/devices/%s/delete" % host.devs[delIdx].scsiAddr)
            step.setRC(RC.OK, "<mark>Delete %s disk</mark>" % host.devs[delIdx].scsiAddr)

    def _rdiskRandDel(self, step):
        # delete one pDisk
        for host in self.bench.getDockHosts():

            delIdx = random.randint(0, len(host.devs) - 1)
            host.run("echo 1 > /sys/bus/scsi/devices/%s/delete" % host.devs[delIdx].scsiAddr)
            step.setRC(RC.OK, "<mark>Delete %s disk</mark>" % host.devs[delIdx].scsiAddr)

    def _rdiskMax(self, step):
        devCnt = step.opq
        step.opq = TcBase.DEV_TYPE.RAW
        self._getDeviceList(step)

        # delete one pDisk
        for host in self.bench.getDockHosts():
            for devIdx in range(len(host.devs)):
                if devIdx < devCnt:
                    continue
                host.run("echo 1 > /sys/bus/scsi/devices/%s/delete" % host.devs[devIdx].scsiAddr)

    def _rdiskRescan(self, step):
        for host in self.bench.getDockHosts():
            host.run("/bin/rescan-scsi-bus.sh -a -w")

    def _setIoScheduler(self, step):
        if step.opq is None:
            scheduler = 'cfq'
        else:
            scheduler = step.opq.lower()
            if scheduler != 'noop' and scheduler != 'deadline' and scheduler != 'cfq':
                step.setRC(RC.ERROR, "Invalid IO scheduler name %s", step.opq)
                return

        for host in self.bench.getDockHosts():
            for dev in host.devs:
                host.run("echo %s > /sys/block/%s/queue/scheduler" % (scheduler, dev.devName[5:]))

    def _secureErase(self, step):
        target = step.opq
        for host in self.bench.getDockHosts():
            for devIdx in range(len(host.devs)):
                if target is not None and target != devIdx:
                    continue
                dev = host.devs[devIdx]
                host.run('hdparm -I %s' % dev.devName)
                frozenState, notSupport, securityEnable = host.getRslt()

                if notSupport:
                    step.setRC( RC.ERROR, "Enhanced erase is not supported")
                    return
                elif frozenState:
                    step.setRC( RC.ERROR, "SSD in frozen state" )
                    return
                elif securityEnable:
                    step.setRC( RC.WARNING, "security feature enabled already")
                else:

                    host.run('hdparm --user-master u --security-set-pass kodiak %s' % dev.devName)

                    host.run('hdparm -I %s' % dev.devName)
                    frozenState, notSupport, securityEnable = host.getRslt()
                    if not securityEnable:
                        step.setRC( RC.ERROR, "Failed to enable security feature")
                        return
    
                host.run('hdparm --user-master u --security-erase kodiak %s' % dev.devName)
                host.run('hdparm -I %s' % dev.devName)
                frozenState, notSupport, securityEnable = host.getRslt()
                if securityEnable:
                    step.setRC( RC.WARNING, "Failed to disable security feature")
                    return
                else:
                    self.addNotice(step, "Success security erase %s device" % dev.devName) 

    def _rbdStatus(self, step):
        for host in self.bench.getDockHosts():
            host.run('/bin/grep "Rebuild" /var/log/kodiak/consoleDH.log | cut -d":" -f6')
            if host.getRslt() is None:
                step.setRC(RC.WARNING, "No rebuild status")
            else:
                step.setRC(RC.OK, "<mark>%s</mark>" % host.getRslt()[-1])

    def _startCheck(self, step):
        wlist = step.opq
        idx   = -1
        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            TcHelper.waitTill(host, self.bench.debugLog, 'Process registry started|Dock resources are null')
            if host.getRC() != RC.OK:
                step.setRC(RC.ERROR, "Failed to start the kdhmgr in %d seconds" % waitTime)
                return
            
        # @todo check Process registry starting on port
        idx   = -1
        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('/bin/curl http://localhost:3000/kodiak/api/dockhost/resources > /tmp/kodiak_res.xml')
            host.run('/bin/grep --color=never uptime /tmp/kodiak_res.xml')
            if host.getRC() != RC.OK:
                step.setRC(RC.ERROR, 'Kodiak apps have some issues at %s' % host) ;
                return
                
        idx   = -1
        for host in self.bench.getAppHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('pidof node')
            host.run('echo $?')
            if host.getRC() == RC.ERROR:
                step.setRC(RC.ERROR, 'dockport is not running at %s' % host) ;
                return

            host.run('lsmod | grep kodiak')
            if host.getRslt() is None:
                step.setRC(RC.ERROR, 'mod kodiak is not running at %s' % host) ;
                return

        step.setRC(RC.OK)
        return

    def _stopAll(self, step):
        wlist = step.opq

        idx   = -1
        for host in self.bench.getAppHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('/bin/systemctl is-active kodiak-data-engine')
            if host.getRslt():
                host.run('/bin/systemctl stop kodiak-data-engine')

        idx   = -1
        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('/bin/systemctl is-active kodiak-data-engine')
            if host.getRslt():
                host.run('/bin/systemctl stop kodiak-data-engine')

        step.setRC(RC.OK)
        return

    def _stopCheck(self, step):
        wlist = step.opq

        time.sleep(10)
        idx   = -1
        for host in self.bench.getAppHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('pidof node')
            host.run('echo $?')
            if host.getRC() == RC.OK:
                step.setRC(RC.ERROR, 'Kodiak apps are still running at %s' % host) ;
                return

        idx   = -1
        for host in self.bench.getDockHosts():
            idx += 1
            if wlist is not None and idx not in wlist:
                continue

            host.run('pidof node')
            host.run('echo $?')
            if host.getRC() == RC.OK:
                step.setRC(RC.ERROR, 'Kodiak apps are still running at %s' % host) ;
                return
        return

    def _reset(self, step):
        resetDock, resetAll = step.opq
        
        for host in self.bench.getDockHosts():
            host.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/mnt/*/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/cfg/poolkeeper/tilekeeper/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/cfg/poolkeeper/tilepanel/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/cfg/tilekeeper/*' % self.bench.getDockName())

            if resetDock:
                host.run('/bin/umount /kodiak/dock/%s/docknode/*/mnt/*' % self.bench.getDockName())
                host.run('/bin/rm -rf /kodiak/dock/%s/* ' \
                                     '/kodiak/dockhost/dock/%s ' \
                                     '/kodiak/dockport/dockport.cfg' %
                         (self.bench.getDockName(), self.bench.getDockName()))
            if resetAll:
                host.run('/bin/rm -rf /kodiak/dockhost/resources.cfg ' \
                                     '/kodiak/dockhost/mount.cfg '\
                                     '/kodiak/dockhost/host_binding.cfg ' \
                                     '/kodiak/dockport/dockport.cfg')
        for host in self.bench.getAppHosts():

            if resetDock:
                host.run('/bin/rm -rf /kodiak/dock/%s/* ' \
                                 '/kodiak/dockhost/dock/%s ' \
                                 '/kodiak/dockport/dockport.cfg' %
                     (self.bench.getDockName(), self.bench.getDockName()))
            if resetAll:
                host.run('/bin/rm -rf /kodiak/dockhost/resources.cfg ' \
                                     '/kodiak/dockhost/mount.cfg '\
                                     '/kodiak/dockhost/host_binding.cfg ' \
                                     '/kodiak/dockport/dockport.cfg')

    def _resetTkcd(self, step):
        nodeId = step.opq
        for host in self.bench.getDockHosts():
            for node in host.nodes:
                if step.opq is not None and node.nodeId != step.opq:
                    continue
                self.local.run('/bin/rm /kodiak/dock/%s/docknode/%d/cfg/tilekeeper/tile.db' %
                               ( self.bench.getDockName(), node.nodeId ) ) ;
        self.local.run('/bin/rm -rf /kodiak/dock/%s/docknode/*/mnt/*/*.data' %
                self.bench.getDockName())

    def _backupTkcd(self, step):
        for host in self.bench.getDockHosts():
            for node in host.nodes:
                self.local.run('/bin/cp /kodiak/dock/%s/docknode/%d/cfg/tilekeeper/tile.db ' \
                                       '/kodiak/dock/%s/docknode/%d/cfg/tilekeeper/tile.db.bak' %
                               ( self.bench.getDockName(), node.nodeId,
                                 self.bench.getDockName(), node.nodeId ) ) ;

    def _restoreTkcd(self, step):
        for host in self.bench.getDockHosts():
            for node in host.nodes:
                self.local.run('/bin/cp /kodiak/dock/%s/docknode/%d/cfg/tilekeeper/tile.db.bak ' \
                                       '/kodiak/dock/%s/docknode/%d/cfg/tilekeeper/tile.db' %
                               ( self.bench.getDockName(), node.nodeId,
                                 self.bench.getDockName(), node.nodeId ) ) ;

    def _initAll(self, step):
        for host in self.bench.getDockHosts():
            host.run('/bin/umount /kodiak/dock/%s/docknode/*/mnt/*' % self.bench.getDockName())
            host.run('/bin/rm -rf /kodiak/dock/* %s %s %s %s' %
                     ('/kodiak/dockhost/dock.cfg', '/kodiak/dockhost/xfs.cfg',
                      '/kodiak/dockhost/resources.cfg', '/kodiak/dockport/dockport.cfg' ))
            host.run('/home/kodiak/scripts/install.sh << END\n%s\n%s\n%s\n%s\n\nEND' %
                     ("Yes\nYes\nYes\nYes\nYes\nYes\nYes\nYes",
                      "Yes\nNo\nYes\nYes",
                      self.bench.getDockName(),
                      self.bench.getBrokerAddr()))

        for host in self.bench.getAppHosts():
            host.run('/bin/rm -rf /kodiak/dock/* %s %s %s %s' %
                     ('/kodiak/dockhost/dock.cfg', '/kodiak/dockhost/xfs.cfg',
                      '/kodiak/dockhost/resources.cfg', '/kodiak/dockport/dockport.cfg' ))
            host.run('/home/kodiak/scripts/install.sh << END\n%s\n%s\n%s\n\nEND' %
                     ("Yes\nNo\nYes\nYes",
                      self.bench.getDockName(),
                      self.bench.getBrokerAddr()))

    def _hello(self, step):
        for host in self.bench.getDockHosts():
            host.run('echo hello %s' % host.urlStr) ;

        for host in self.bench.getAppHosts():
            host.run('echo hello') ;

if __name__ == '__main__':
    ''' Test this module here '''


