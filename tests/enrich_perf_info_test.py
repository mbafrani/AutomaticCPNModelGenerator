import unittest
import sys
import os

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.util import exec_utils, xes_constants, constants as pm4py_constants
from pm4py.algo.filtering.log.attributes import attributes_filter
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from api.models import PetriNet, PetriNetPerformanceEnricher


def mine_petrinet(path):
    log = xes_importer.apply(path)
    net, im, fm = inductive_miner.apply(log)
    petrinet = PetriNet(log, net, im, fm)
    return petrinet, log, net, im, fm


class Parameters(Enum):
    ACTIVITY_KEY = pm4py_constants.PARAMETER_CONSTANT_ACTIVITY_KEY


base_path = os.path.join(os.path.dirname(__file__), "data", "input")
interval_event_log_path = os.path.join(base_path, "interval_event_log.xes")
one_timestamp_log_example_path = os.path.join(base_path, "event-log.xes")
act_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, {}, xes_constants.DEFAULT_NAME_KEY)


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
        self.assertEqual(len(stats_mean), 10)
        self.assertEqual(len(stats_stdev), 10)
        self.assertIn("decide", stats_mean)
        self.assertAlmostEqual(stats_mean['decide'], 4564.27, 2)
        self.assertIn("decide", stats_stdev)
        self.assertAlmostEqual(stats_stdev['decide'], 3309.835, 3)
        self.assertIn("register request", stats_mean)
        self.assertEqual(stats_mean['register request'], 0)
        self.assertIn("register request", stats_stdev)
        self.assertEqual(stats_stdev['register request'], 0)

    def test_get_resource_capacity_logs_with_resources(self):
        petrinet, log, net, im, fm = mine_petrinet(one_timestamp_log_example_path)
        activities = list(attributes_filter.get_attribute_values(log, act_key))
        enricher = PetriNetPerformanceEnricher(petrinet)
        res_capacity_dict = enricher._get_res_capacities(log, activities)
        self.assertEqual(len(res_capacity_dict), len(activities))
        self.assertIn("register request", res_capacity_dict)
        self.assertEqual(res_capacity_dict['register request'], 3)
        self.assertIn("decide", res_capacity_dict)
        self.assertEqual(res_capacity_dict['decide'], 1)

    def test_get_resource_capacity_logs_without_resources(self):
        petrinet, log, net, im, fm = mine_petrinet(interval_event_log_path)
        activities = list(attributes_filter.get_attribute_values(log, act_key))
        enricher = PetriNetPerformanceEnricher(petrinet)
        res_capacity_dict = enricher._get_res_capacities(log, activities)
        self.assertEqual(len(res_capacity_dict), len(activities))
        self.assertIn("place order", res_capacity_dict)
        self.assertEqual(res_capacity_dict['place order'], 1)
        self.assertIn("cancel order", res_capacity_dict)
        self.assertEqual(res_capacity_dict['cancel order'], 1)


if __name__ == "__main__":
    t = TestEnrichPerfInfo()
    t.test_interval_event_log()
    t.test_one_timestamp_event_log()
    unittest.main()
