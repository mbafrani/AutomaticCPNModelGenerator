import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import flask
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from api.services import EventLogService
from api.util import constants


class TestEventLogService(unittest.TestCase):

    # region test_allowed_file

    def test_allowed_file__false(self):
        file_name = "dummy.txt"
        is_allowed = EventLogService.allowed_file(file_name)
        self.assertFalse(is_allowed)

    def test_allowed_file__xes(self):
        file_name = "dummy.xes"
        is_allowed = EventLogService.allowed_file(file_name)
        self.assertTrue(is_allowed)

    def test_allowed_file__csv(self):
        file_name = "dummy.csv"
        is_allowed = EventLogService.allowed_file(file_name)
        self.assertTrue(is_allowed)

    # endregion

    # region save_log_file

    def test_save_log_file__file_not_found(self):
        event_log_service = EventLogService()
        file_obj = MagicMock()
        file_obj.filename = ""
        with self.assertRaises(NotFound) as ex:
            event_log_service.save_log_file(file_obj)
        self.assertEqual(constants.ERROR_FILE_NOT_FOUND_IN_REQUEST, str(ex.exception.description))

    def test_save_log_file__file_not_allowed(self):
        event_log_service = EventLogService()
        file_obj = MagicMock()
        file_obj.filename = "dummy.txt"
        with self.assertRaises(UnsupportedMediaType) as ex:
            event_log_service.save_log_file(file_obj)
        self.assertEqual(constants.ERROR_INVALID_FILE, str(ex.exception.description))

    # endregion


if __name__ == '__main__':
    unittest.main()
