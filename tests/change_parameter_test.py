import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from api.util.constants import RequestJsonKeys, PetriNetDictKeys
from app import app


class test_parameter_change(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(test_parameter_change, self).__init__(*args, **kwargs)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def check_transition_data(self, transitions, trans_name, exp_mean, exp_std, exp_res_capacity):
        self.assertIn(trans_name, transitions)
        trans = transitions[trans_name][PetriNetDictKeys.performance]
        self.assertIn(PetriNetDictKeys.mean, trans)
        self.assertIn(PetriNetDictKeys.std, trans)
        self.assertIn(PetriNetDictKeys.res_capacity, trans)
        mean = trans[PetriNetDictKeys.mean]
        std = trans[PetriNetDictKeys.std]
        res_capacity = trans[PetriNetDictKeys.res_capacity]
        self.assertAlmostEqual(mean, exp_mean, 2)
        self.assertAlmostEqual(std, exp_std, 2)
        self.assertEqual(res_capacity, exp_res_capacity)

    def check_decision_point_data(self, places, name, probs):
        self.assertIn(name, places)
        dp = places[name][PetriNetDictKeys.frequencies]
        for key, value in dp.items():
            self.assertAlmostEqual(probs.get(key), value, 2)

    def test_parameter_change(self):
        # 1. File upload
        file_name = "ETM_Configuration1.xes"
        path = os.path.join(os.path.dirname(__file__), "data", "input", file_name)

        file = open(path, "rb")
        data = {"file": (file, file_name)}
        response = self.client.post(
            "api/event-log", content_type="multipart/form-data", data=data
        )
        self.assertIn(b"Event log uploaded successfully", response.data)
        event_log_id = response.json.get(RequestJsonKeys.event_log_id)
        self.assertIsNotNone(event_log_id)

        # 2. Check Enrichments
        data = {RequestJsonKeys.event_log_id: event_log_id, "test": True}
        response = self.client.post("api/process-model/enrichment-dict", json=data)

        transitions = response.json[PetriNetDictKeys.transitions]
        places = response.json[PetriNetDictKeys.places]
        arrival_rate = response.json[PetriNetDictKeys.net][PetriNetDictKeys.arrivalrate]

        self.check_transition_data(transitions, "A", 0, 0, 1)
        self.check_transition_data(transitions, "B", 6.12, 4.19, 1)
        self.check_transition_data(transitions, "C", 12.01, 5.64, 1)
        self.check_transition_data(transitions, "D", 11.87, 4.71, 1)
        self.check_transition_data(transitions, "E", 4.15, 2.86, 1)
        self.check_transition_data(transitions, "F", 4.7, 2.82, 1)
        self.check_transition_data(transitions, "G", 4.98, 2.8, 1)

        self.check_decision_point_data(places, "p_9", {"D": 0.9, "skip_3": 0.1})
        self.check_decision_point_data(places, "p_4", {"E": 0.2, "F": 0.8})
        self.assertEqual(arrival_rate, 6)

        # 3. Update transition, check correct update
        data = {
            RequestJsonKeys.event_log_id: event_log_id,
            RequestJsonKeys.arrivalrate: 10,
            "test": True,
            RequestJsonKeys.transitions: [
                {
                    RequestJsonKeys.transition: "B",
                    RequestJsonKeys.mean: 3,
                    RequestJsonKeys.std: 3,
                    RequestJsonKeys.res_capacity: 5,
                }]
        }
        response = self.client.post("api/change-parameter", json=data)
        transitions = response.json[PetriNetDictKeys.transitions]
        self.check_transition_data(transitions, "B", 3, 3, 5)

        # 4. Check if the update is saved on the server
        data = {RequestJsonKeys.event_log_id: event_log_id, "test": True}
        response = self.client.post("api/process-model/enrichment-dict", json=data)
        transitions = response.json[PetriNetDictKeys.transitions]
        self.check_transition_data(transitions, "B", 3, 3, 5)
        self.assertEqual(response.json[PetriNetDictKeys.net][PetriNetDictKeys.arrivalrate], 10)


if __name__ == "__main__":
    t = test_parameter_change()
    t.test_parameter_change()
    unittest.main()
