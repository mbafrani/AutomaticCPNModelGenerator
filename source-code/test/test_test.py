import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app


class test_something(unittest.TestCase):
    def __init__(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_something(self):
        file_name = "ETM_Configuration1.xes"
        path = os.path.join("source-code/test/input_data/", file_name)
        
        file = open(path, "rb")

        data = {"file": (file, file_name)}
        
        response = self.client.post(
            "/event-log", content_type="multipart/form-data", data=data
        )
        self.assertIn(b"Event log uploaded successfully", response.data)
        event_log_id = response.json.get("event_log_id")
        self.assertIsNotNone(event_log_id)

        data = {"event_log_id" : event_log_id}
        self.client.post("/process-model", data=data)
        a = 3


if __name__ == "__main__":
    t = test_something()
    t.test_something()
    unittest.main()
