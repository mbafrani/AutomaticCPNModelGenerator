import unittest
import sys
import os

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.sojourn_time.log import get as soj_time_get

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from models import PetriNet, PetriNetPerformanceEnricher  # noqa: E402


def mine_petrinet(path):
    log = xes_importer.apply(path)
    net, im, fm = inductive_miner.apply(log)
    petrinet = PetriNet(log, net, im, fm)
    return petrinet, log, net, im, fm


base_path = os.path.join(os.path.dirname(__file__), "input_data")
interval_event_log_path = os.path.join(base_path, "interval_event_log.xes")
one_timestamp_log_example_path = os.path.join(base_path, "event-log.xes")


class TestEnrichPerfInfo(unittest.TestCase):
    def test_interval_event_log(self):
        petrinet, log, net, im, fm = mine_petrinet(interval_event_log_path)
        enricher = PetriNetPerformanceEnricher(petrinet)
        duration_dict_mean, duration_dict_stdev \
            = enricher._get_service_time_two_timestamps(log, parameters={
                soj_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
                soj_time_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})
        self.assertEqual(len(duration_dict_mean), len(duration_dict_stdev))
        self.assertEqual(len(duration_dict_mean), 8)
        self.assertEqual(len(duration_dict_stdev), 8)
        self.assertIn("place order", duration_dict_mean)
        self.assertAlmostEqual(duration_dict_mean['place order'], 42.03, 2)
        self.assertIn("place order", duration_dict_stdev)
        self.assertAlmostEqual(duration_dict_stdev['place order'], 74.24, 2)

    def test_one_timestamp_event_log(self):
        petrinet, log, net, im, fm = mine_petrinet(one_timestamp_log_example_path)
        enricher = PetriNetPerformanceEnricher(petrinet)
        stats_mean, stats_stdev \
            = enricher._get_service_time_single_timestamps(log, net, im, fm)
        self.assertEqual(len(stats_mean), len(stats_stdev))
        self.assertEqual(len(stats_mean), 8)
        self.assertEqual(len(stats_stdev), 8)
        self.assertIn("decide", stats_mean)
        self.assertAlmostEqual(stats_mean['decide'], 4564.27, 2)
        self.assertIn("decide", stats_stdev)
        self.assertAlmostEqual(stats_stdev['decide'], 3309.835, 3)
        self.assertIn("register request", stats_mean)
        self.assertEqual(stats_mean['register request'], 0)
        self.assertIn("register request", stats_stdev)
        self.assertEqual(stats_stdev['register request'], 0)


if __name__ == "__main__":
    t = TestEnrichPerfInfo()
    t.test_interval_event_log()
    t.test_one_timestamp_event_log()
    unittest.main()
