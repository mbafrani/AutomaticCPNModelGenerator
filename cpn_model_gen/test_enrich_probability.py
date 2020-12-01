from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from enrich_probability import (
    get_successor_frequencies,
    enrich_petrinet_decision_probabilities,
    get_decision_points_from_net,
    dict_key,
)


import unittest


def mine_petrinet(path):
    # Discover Net
    log = xes_importer.apply(path)
    net, init_marking, final_marking = inductive_miner.apply(log)
    return log, net, init_marking, final_marking


em_configuration1_path = "cpn_model_gen/input_data/ETM_Configuration1.xes"
em_configuration2_path = "cpn_model_gen/input_data/ETM_Configuration2.xes"
running_example_path = "cpn_model_gen/input_data/running-example.xes"


class test_enrich_probability(unittest.TestCase):
    def test_etm_configuration1(self):
        log, net, im, fm = mine_petrinet(em_configuration1_path)
        enrich_petrinet_decision_probabilities(log, net, im, fm)
        dps = list(get_decision_points_from_net(net))
        self.assertEqual(len(dps), 2)
        dp_dict = {dp.name: dp for dp in dps}
        self.assertIn("p_4", dp_dict)
        self.assertIn("p_9", dp_dict)

        p4 = dp_dict["p_4"]
        freq_dict = p4.properties[dict_key]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["E"], 0.2)
        self.assertAlmostEqual(freq_dict["F"], 0.8)

        p9 = dp_dict["p_9"]
        freq_dict = p9.properties[dict_key]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["D"], 0.9)
        self.assertAlmostEqual(freq_dict["skip_3"], 0.1)

    def test_etm_configuration2(self):
        log, net, im, fm = mine_petrinet(em_configuration2_path)
        enrich_petrinet_decision_probabilities(log, net, im, fm)
        dps = list(get_decision_points_from_net(net))
        self.assertEqual(len(dps), 1)
        dp_dict = {dp.name: dp for dp in dps}
        self.assertIn("p_7", dp_dict)

        p7 = dp_dict["p_7"]
        freq_dict = p7.properties[dict_key]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["E"], 0.29, 2)
        self.assertAlmostEqual(freq_dict["F"], 0.71, 2)

    def test_running_example(self):
        log, net, im, fm = mine_petrinet(running_example_path)
        enrich_petrinet_decision_probabilities(log, net, im, fm)
        dps = list(get_decision_points_from_net(net))
        self.assertEqual(len(dps), 3)
        dp_dict = {dp.name: dp for dp in dps}
        self.assertIn("p_4", dp_dict)
        self.assertIn("p_6", dp_dict)
        self.assertIn("p_10", dp_dict)

        dp = dp_dict["p_4"]
        freq_dict = dp.properties[dict_key]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["reject request"], 0.50, 2)
        self.assertAlmostEqual(freq_dict["pay compensation"], 0.50, 2)

        dp = dp_dict["p_6"]
        freq_dict = dp.properties[dict_key]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["skip_5"], 0.67, 2)
        self.assertAlmostEqual(freq_dict["reinitiate request"], 0.33, 2)

        dp = dp_dict["p_10"]
        freq_dict = dp.properties[dict_key]
        self.assertEqual(len(freq_dict), 2)
        self.assertAlmostEqual(freq_dict["examine thoroughly"], 0.33, 2)
        self.assertAlmostEqual(freq_dict["examine casually"], 0.67, 2)


if __name__ == "__main__":
    unittest.main()
