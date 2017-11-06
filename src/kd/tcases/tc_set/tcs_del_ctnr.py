#! /usr/bin/env python


from kd.tfwk.test_set import TestSet
import kd.tcases

class TcsDelCtnr(TestSet):

    def __init__(self, whitelist=['P_none', 'P_4x1_32k', 'P_8x1_8k'], blacklist=[]):
        desc = 'Delete container'
        super(TcsDelCtnr, self).__init__(desc)

        self.whitelist = whitelist
        self.blacklist = blacklist

    def _printDesc(self, step):
        pass

    def _getTestSpecs(self):
        specs = []

        specs.append( kd.tcases.helper.tch_dhost.TchDhost('rdisk-rescan') )
        specs.append( kd.tcases.tc_set.tcs_simple.TcsSimple('restartAndReset') )
        specs.append( kd.tcases.tc_set.tcs_simple.TcsSimple('dockResBindingCfg') )
# test dock
        for pType in self.whitelist:
            if pType in self.blacklist:
                continue
            specs.append( kd.tcases.dock.tc_dock_ctnr.TcDockCtnr(['Ctnr_%s_1' % pType,[ 8] * 3, pType]) )
            specs.append( kd.tcases.dock.tc_dock_ctnr.TcDockCtnr(['Ctnr_%s_2' % pType,[16] * 3, pType]) )

        specs.append( kd.tcases.io.tc_io_tile.TcIoTile( ) )
        specs.append( kd.tcases.helper.tch_util.TchUtil('sleep', 120) )

        for pType in self.whitelist:
            if pType in self.blacklist:
                continue
            specs.append( kd.tcases.dock.tc_dock_ctnr.TcDockCtnr(['Ctnr_%s_2' % pType]) )
        specs.append( kd.tcases.io.tc_io_tile.TcIoTile( ) )

        return specs


