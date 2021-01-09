from flask import current_app
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest
from werkzeug.utils import secure_filename
import os
import uuid

from api.util import constants
from api.models import EventLog, PetriNet


class EventLogService:
    @staticmethod
    def delete_log_file(event_log_id):
        path = EventLogService.get_log_file_path(event_log_id)
        os.remove(path)

    @staticmethod
    def _gen_path_without_extension(event_log_id):
        base_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            event_log_id,
            current_app.config["EVENT_LOG_DEFAULT_NAME"] + "."
        )
        return base_path

    @staticmethod
    def get_log_file_path(event_log_id):
        base_path = EventLogService._gen_path_without_extension(event_log_id)
        extensions = [constants.XES_EXTENSION, constants.CSV_EXTENSION]
        log_file_path = None
        for extension in extensions:
            log_file_path = base_path + extension
            if os.path.isfile(log_file_path):
                break

        if log_file_path is None:
            raise NotFound(constants.ERROR_EVENT_LOG_DOESNT_EXIST)
            
        return log_file_path
        
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

            # Check if the file contents are empty
            if (os.stat(tmp_file_path).st_size == 0):
                raise BadRequest(constants.ERROR_INVALID_FILE)

            os.makedirs(
                os.path.join(current_app.config['UPLOAD_FOLDER'], event_log_id)
            )
            new_file_path = EventLogService._gen_path_without_extension(event_log_id)
            new_file_path += file_extension
            os.rename(tmp_file_path, new_file_path)

            return EventLog(event_log_id, file_extension)
        else:
            raise UnsupportedMediaType(constants.ERROR_INVALID_FILE)
