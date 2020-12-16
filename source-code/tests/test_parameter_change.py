import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from util.constants import RequestJsonKeys, PetriNetDictKeys
from app import app


class test_parameter_change(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(test_parameter_change, self).__init__(*args, **kwargs)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def check_transition_data(self, transitions, trans_name, exp_mean, exp_std):
        self.assertIn(trans_name, transitions)
        trans = transitions[trans_name][PetriNetDictKeys.performance]
        self.assertIn(PetriNetDictKeys.mean, trans)
        self.assertIn(PetriNetDictKeys.std, trans)
        mean = trans[PetriNetDictKeys.mean]
        std = trans[PetriNetDictKeys.std]
        self.assertAlmostEqual(mean, exp_mean, 2)
        self.assertAlmostEqual(std, exp_std, 2)

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
            "/event-log", content_type="multipart/form-data", data=data
        )
        self.assertIn(b"Event log uploaded successfully", response.data)
        event_log_id = response.json.get(RequestJsonKeys.event_log_id)
        self.assertIsNotNone(event_log_id)

        # 2. Check Enrichments
        data = {RequestJsonKeys.event_log_id: event_log_id, "test": True}
        response = self.client.post("/process-model", json=data)

        transitions = response.json["transitions"]
        places = response.json["places"]

        self.check_transition_data(transitions, "A", 0, 0)
        self.check_transition_data(transitions, "B", 6.12, 4.19)
        self.check_transition_data(transitions, "C", 12.01, 5.64)
        self.check_transition_data(transitions, "D", 11.87, 4.71)
        self.check_transition_data(transitions, "E", 4.15, 2.86)
        self.check_transition_data(transitions, "F", 4.7, 2.82)
        self.check_transition_data(transitions, "G", 4.98, 2.8)

        self.check_decision_point_data(places, "p_9", {"D": 0.9, "skip_3": 0.1})
        self.check_decision_point_data(places, "p_4", {"E": 0.2, "F": 0.8})

        # 3. Update transition, check correct update
        data = {
            RequestJsonKeys.event_log_id: event_log_id,
            "test": True,
            RequestJsonKeys.transition: "B",
            RequestJsonKeys.mean: 3,
            RequestJsonKeys.std: 3,
        }
        response = self.client.post("/change-transition", json=data)
        transitions = response.json[PetriNetDictKeys.transitions]
        self.check_transition_data(transitions, "B", 3, 3)

        # 4. Update decision point, check correct update
        frequencies = {"D": 0.8, "skip_3": 0.2}
        data = {
            RequestJsonKeys.event_log_id: event_log_id,
            "test": True,
            RequestJsonKeys.place: "p_9",
            RequestJsonKeys.frequencies: frequencies,
        }
        response = self.client.post("/change-decision-point", json=data)
        places = response.json[PetriNetDictKeys.places]
        self.check_decision_point_data(places, "p_9", frequencies)

        # 5. Check if the update is saved on the server
        data = {RequestJsonKeys.event_log_id: event_log_id, "test": True}
        response = self.client.post("/process-model", json=data)
        transitions = response.json[PetriNetDictKeys.transitions]
        places = response.json[PetriNetDictKeys.places]
        self.check_decision_point_data(places, "p_9", frequencies)
        self.check_transition_data(transitions, "B", 3, 3)


if __name__ == "__main__":
    t = test_parameter_change()
    t.test_parameter_change()
    unittest.main()
