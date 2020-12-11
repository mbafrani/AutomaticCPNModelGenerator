import unittest
import sys
import os

import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.log import EventLog
from pm4py.objects.petri.petrinet import PetriNet

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from models import PetriNet

input_data_path = os.path.join(os.path.dirname(__file__), "data", "input")


class TestPetriNet(unittest.TestCase):
    def test_importing_xes(self):
        obj = PetriNet()
        self.assertTrue(os.path.exists(os.path.join(input_data_path, "event-log.xes")))
        log_func = obj.import_xes_log(os.path.join(input_data_path, "event-log.xes"))
        log_lib = xes_importer.apply(os.path.join(input_data_path, "event-log.xes"))
        self.assertEqual(len(log_func), len(log_lib))
        self.assertGreater(len(log_func), 0, "Empty log file")
        self.assertIsInstance(log_func, EventLog, "Not an instance of EventLog")

    def test_importing_csv(self):
        obj = PetriNet()
        self.assertTrue(os.path.exists(os.path.join(input_data_path, "event-log.csv")))
        log_func = obj.import_csv_log(os.path.join(input_data_path, "event-log.csv"))
        self.assertGreater(len(log_func), 0, "Empty log file")
        self.assertIsInstance(log_func, EventLog, "Not an instance of EventLog")

    def test_discover_process_model(self):
        log_lib = xes_importer.apply(os.path.join(input_data_path, "event-log.xes"))
        obj = PetriNet(log_lib)
        net, im, fm = obj.discover_process_model()
        self.assertEqual(len(im), 1)
        self.assertEqual(len(fm), 1)
        self.assertIsInstance(net, pm4py.objects.petri.petrinet.PetriNet,
                              "Not an instance of Petrinet")
        self.assertGreater(len(net.places), 0, "No places in the petri net")
        self.assertGreater(len(net.arcs), 0, "No arcs in the petri net")
        self.assertGreater(len(net._PetriNet__transitions), 0,
                           "No transitions in the petri net")


if __name__ == '__main__':
    unittest.main()
