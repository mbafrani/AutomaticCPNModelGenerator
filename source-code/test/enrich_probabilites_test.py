import os
import unittest
import sys

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "models"))
from models import PetriNet  # noqa: E402

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "..", "src", "util"))
from util import constants   # noqa: E402


def mine_petrinet(path):
    # Discover Net
    log = xes_importer.apply(path)
    net, init_marking, final_marking = inductive_miner.apply(log)
    petrinet = PetriNet(log, net, init_marking, final_marking)
    return petrinet


base_path = os.path.join(os.path.dirname(__file__), "input_data")
em_configuration1_path = os.path.join(base_path, "ETM_Configuration1.xes")
em_configuration2_path = os.path.join(base_path, "ETM_Configuration2.xes")
running_example_path = os.path.join(base_path, "running-example.xes")


class test_enrich_probability(unittest.TestCase):
    def test_etm_configuration1(self):
        petrinet = mine_petrinet(em_configuration1_path)
        dps = petrinet.enrich_petrinet_decision_probabilities()

        self.assertEqual(len(dps), 2)
        dp_dict = {dp.name: dp for dp in dps}
        self.assertIn("p_4", dp_dict)
        self.assertIn("p_9", dp_dict)

        p4 = dp_dict["p_4"]
        freq_dict = p4.properties[constants.DICT_KEY_FREQUENCY]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["E"], 0.2)
        self.assertAlmostEqual(freq_dict["F"], 0.8)

        p9 = dp_dict["p_9"]
        freq_dict = p9.properties[constants.DICT_KEY_FREQUENCY]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["D"], 0.9)
        self.assertAlmostEqual(freq_dict["skip_3"], 0.1)

    def test_etm_configuration2(self):
        petrinet = mine_petrinet(em_configuration2_path)
        dps = petrinet.enrich_petrinet_decision_probabilities()
        self.assertEqual(len(dps), 1)
        dp_dict = {dp.name: dp for dp in dps}
        self.assertIn("p_7", dp_dict)

        p7 = dp_dict["p_7"]
        freq_dict = p7.properties[constants.DICT_KEY_FREQUENCY]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["E"], 0.29, 2)
        self.assertAlmostEqual(freq_dict["F"], 0.71, 2)

    def test_running_example(self):
        petrinet = mine_petrinet(running_example_path)
        dps = petrinet.enrich_petrinet_decision_probabilities()
        self.assertEqual(len(dps), 3)
        dp_dict = {dp.name: dp for dp in dps}
        self.assertIn("p_4", dp_dict)
        self.assertIn("p_6", dp_dict)
        self.assertIn("p_10", dp_dict)

        dp = dp_dict["p_4"]
        freq_dict = dp.properties[constants.DICT_KEY_FREQUENCY]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["reject request"], 0.50, 2)
        self.assertAlmostEqual(freq_dict["pay compensation"], 0.50, 2)

        dp = dp_dict["p_6"]
        freq_dict = dp.properties[constants.DICT_KEY_FREQUENCY]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["skip_5"], 0.67, 2)
        self.assertAlmostEqual(freq_dict["reinitiate request"], 0.33, 2)

        dp = dp_dict["p_10"]
        freq_dict = dp.properties[constants.DICT_KEY_FREQUENCY]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["examine thoroughly"], 0.33, 2)
        self.assertAlmostEqual(freq_dict["examine casually"], 0.67, 2)


if __name__ == "__main__":
    unittest.main()
