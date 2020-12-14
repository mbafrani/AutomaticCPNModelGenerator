from flask import current_app
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest
from werkzeug.utils import secure_filename
import os
import uuid

from util import constants
from models import EventLog, PetriNet


class EventLogService:

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in constants.ALLOWED_EXTENSIONS

    @staticmethod
    def is_event_log_id_feasible(event_log_id):
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], event_log_id)
        return os.path.exists(path)

    @staticmethod
    def save_log_file(file):
        if file.filename == '':
            raise NotFound(constants.ERROR_FILE_NOT_FOUND_IN_REQUEST)
        if file and EventLogService.allowed_file(file.filename):
            file_extension = secure_filename(file.filename).split('.')[1]
            event_log_id = str(uuid.uuid1())

            # Validate the contents of the log file before saving
            tmp_file_path = os.path.join(
                current_app.config['TEMP_FOLDER'],
                event_log_id + "." + file_extension
            )
            # temporarily store the file for processing
            file.save(tmp_file_path)
            try:
                petri_net = PetriNet()
                if file_extension == constants.XES_EXTENSION:
                    petri_net.import_xes_log(tmp_file_path)
                elif file_extension == constants.CSV_EXTENSION:
                    petri_net.import_csv_log(tmp_file_path)
            except Exception:
                raise BadRequest(constants.ERROR_INVALID_FILE)

            # Check if the file contents are empty
            if (os.stat(tmp_file_path).st_size == 0):
                raise BadRequest(constants.ERROR_INVALID_FILE)

            os.makedirs(
                os.path.join(current_app.config['UPLOAD_FOLDER'], event_log_id)
            )
            file_name = current_app.config["EVENT_LOG_DEFAULT_NAME"] + \
                "." + file_extension
            new_file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                event_log_id,
                file_name
            )
            # move the file from temporary folder to uploads folder
            os.rename(tmp_file_path, new_file_path)

            return EventLog(event_log_id, file_extension)
        else:
            raise UnsupportedMediaType(constants.ERROR_INVALID_FILE)
