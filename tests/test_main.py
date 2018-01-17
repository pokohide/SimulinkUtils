import unittest
from lib import flow_decider as FD
from lib import graph_manager as GM
from lib import utils as Utils

class TestMain(unittest.TestCase):

    def test_perf_does_not_raise_error(self):
        raised = False
        try:
            gm = GM.GraphManager("examples/perf.xml")
            gm.run()
            fd = FD.FlowDecider(gm.startBlocks, gm.blockTable, gm.maxRate)
            fd.run()
        except:
            raised = True
        self.assertFalse(raised, "Perf occuerd error.")

    def test_sample_dose_not_raise_error(self):
        raised = False
        try:
            gm = GM.GraphManager("examples/simple_model.xml")
            gm.run()
            fd = FD.FlowDecider(gm.startBlocks, gm.blockTable, gm.maxRate)
            fd.run()
        except:
            raised = True
        self.assertFalse(raised, "Sample occuerd error.")
