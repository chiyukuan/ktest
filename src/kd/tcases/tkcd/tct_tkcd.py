#! /usr/bin/env python

''' ------------------------|  Python SOURCE FILE  |------------------------

The Description of this file.

@copyright: Copyright (c) by Kodiak Data, Inc. All rights reserved.
'''
import time
from kd.util.logger import getLogger
from kd.tkcd.tkcd_msg import getTkcdAddMsg
from kd.tcases.tkcd.tct_base import TctBase

logger = getLogger(__name__)

class TctTkcd(TctBase):

    def __init__(self, cmd, blist=None):

        if cmd.lower() == 'add':
            super(TctTkcd, self).__init__("Create tkcd cluster")

            self.addStep("Create tkcd cluster", self._enableCluster)

        self.blist = blist


    def _enableCluster(self, step):
        # for each tkcd instance
        for host in self.bench.getDockHosts():
            for node in host.nodes:
                
                # find the tkcd server node 
                for shost in self.bench.getDockHosts():
                    for snode in shost.nodes:

                        if node == snode:
                            continue
                        if self.blist is not None and (snode.nodeId, node.nodeId) in self.blist:
                            continue

                        # add tkcd instance to tkcd server
                        msg = getTkcdAddMsg(node.nodeId, host.ip, node.getTkcdPort())
                        print "send %s msg to TKCD.%d" % (msg, snode.nodeId)
                        snode.tkcdCtx.run( msg, tryParse=False, noRsp=True )
                        step.rcMsg = snode.tkcdCtx.getRcMsg()
                        if not step.canContinue():
                            return

        time.sleep( 3 )

