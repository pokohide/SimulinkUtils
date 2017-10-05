import unittest
from lib import graph_manager as GM

class TestGM(unittest.TestCase):

    def setUp(self):
        # print("Set UP")
        self._gm = GM.GraphManager("examples/sample.xml")

    def test_initialize(self):
        self.assertEqual(1, 1)
