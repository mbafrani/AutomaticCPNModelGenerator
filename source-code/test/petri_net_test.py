import unittest

import os

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.log import EventLog

from models import PetriNet


class TestPetriNet(unittest.TestCase):
    def test_importing_xes(self):
        obj = PetriNet()
        self.assertTrue(os.path.exists(os.path.join("input_data", "event-log.xes")))
        log_func = obj.import_xes_log(os.path.join("input_data", "event-log.xes"))
        log_lib = xes_importer.apply(os.path.join("input_data", "event-log.xes"))
        self.assertEqual(len(log_func), len(log_lib))
        self.assertGreater(len(log_func), 0, "Empty log file")
        self.assertIsInstance(log_func, EventLog, "Not an instance of EventLog")

    def test_importing_csv(self):
        obj = PetriNet()
        self.assertTrue(os.path.exists(os.path.join("input_data", "event-log.csv")))
        log_func = obj.import_csv_log(os.path.join("input_data", "event-log.csv"))
        self.assertGreater(len(log_func), 0, "Empty log file")
        self.assertIsInstance(log_func, EventLog, "Not an instance of EventLog")


if __name__ == "__main__":
    unittest.main()
