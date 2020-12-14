import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import flask
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from services import EventLogService
from util import constants


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

    @patch('uuid.uuid1', return_value="12345-6789-abc")
    @patch('models.PetriNet.import_xes_log', side_effect=Exception())
    def test_save_log_file__file_xes_invalid(self, mocked_uuid1, mocked_import_xes_log):
        app = flask.Flask(__name__)
        with app.app_context():
            event_log_service = EventLogService()

            # setup mocks
            file_obj = MagicMock()
            file_obj.filename = "dummy.xes"
            file_obj.save = MagicMock(return_value=True)
            app.config = MagicMock()

            with self.assertRaises(BadRequest) as ex:
                event_log_service.save_log_file(file_obj)
            self.assertEqual(constants.ERROR_INVALID_FILE, str(ex.exception.description))

    @patch('uuid.uuid1', return_value="12345-6789-abc")
    @patch('models.PetriNet.import_xes_log', return_value=True)
    @patch('os.stat', return_value=MagicMock(st_size=0))
    def test_save_log_file__file_empty(self, mocked_uuid1, mocked_import_xes_log, mocked_os_stat):
        app = flask.Flask(__name__)
        with app.app_context():
            event_log_service = EventLogService()

            # setup mocks
            file_obj = MagicMock()
            file_obj.filename = "dummy.xes"
            file_obj.save = MagicMock(return_value=True)
            app.config = MagicMock()

            with self.assertRaises(BadRequest) as ex:
                event_log_service.save_log_file(file_obj)
            self.assertEqual(constants.ERROR_INVALID_FILE, str(ex.exception.description))

    @patch('uuid.uuid1', return_value="12345-6789-abc")
    @patch('models.PetriNet.import_xes_log', return_value=True)
    @patch('os.stat')
    @patch('os.makedirs')
    @patch('os.rename')
    def test_save_log_file__file_xes_allowed(self, mocked_uuid1, mocked_import_xes_log, mocked_os_stat, mocked_os_mkdirs, mocked_os_rename):
        app = flask.Flask(__name__)
        with app.app_context():
            event_log_service = EventLogService()

            # setup mocks
            file_obj = MagicMock()
            file_obj.filename = "dummy.xes"
            file_obj.save = MagicMock(return_value=True)
            app.config = MagicMock()

            event_log = event_log_service.save_log_file(file_obj)
            self.assertEqual("12345-6789-abc", event_log.id)
            self.assertEqual("xes", event_log.filetype)

    @patch('uuid.uuid1', return_value="12345-6789-abc")
    @patch('models.PetriNet.import_csv_log', side_effect=Exception())
    def test_save_log_file__file_csv_invalid(self, mocked_uuid1, mocked_import_csv_log):
        app = flask.Flask(__name__)
        with app.app_context():
            event_log_service = EventLogService()

            # setup mocks
            file_obj = MagicMock()
            file_obj.filename = "dummy.csv"
            file_obj.save = MagicMock(return_value=True)
            app.config = MagicMock()

            with self.assertRaises(BadRequest) as ex:
                event_log_service.save_log_file(file_obj)
            self.assertEqual(constants.ERROR_INVALID_FILE, str(ex.exception.description))

    @patch('uuid.uuid1', return_value="12345-6789-abc")
    @patch('models.PetriNet.import_csv_log', return_value=True)
    @patch('os.stat')
    @patch('os.makedirs')
    @patch('os.rename')
    def test_save_log_file__file_csv_allowed(self, mocked_uuid1, mocked_import_csv_log, mocked_os_stat, mocked_os_mkdirs, mocked_os_rename):
        app = flask.Flask(__name__)
        with app.app_context():
            event_log_service = EventLogService()

            # setup mocks
            file_obj = MagicMock()
            file_obj.filename = "dummy.csv"
            file_obj.save = MagicMock(return_value=True)
            app.config = MagicMock()

            event_log = event_log_service.save_log_file(file_obj)
            self.assertEqual("12345-6789-abc", event_log.id)
            self.assertEqual("csv", event_log.filetype)

    # endregion


if __name__ == '__main__':
    unittest.main()
