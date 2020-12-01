from flask import current_app
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from werkzeug.utils import secure_filename
import os
import uuid

from util import constants
from models import EventLog

class EventLogService:
  
  @staticmethod
  def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in constants.ALLOWED_EXTENSIONS

  @staticmethod
  def save_log_file(file):
    if file.filename == '':
        raise NotFound(constants.ERROR_FILE_NOT_FOUND_IN_REQUEST)
    if file and EventLogService.allowed_file(file.filename):
        # TODO: Validate the log file before saving

        file_extension = secure_filename(file.filename).split('.')[1]
        folder_name = str(uuid.uuid1())
        os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], folder_name))
        file.save(
          os.path.join(
            current_app.config['UPLOAD_FOLDER'], 
            folder_name, 
            current_app.config["EVENT_LOG_DEFAULT_NAME"] + "." + file_extension
          )
        )
        return EventLog(folder_name, file_extension)
    else:
      raise UnsupportedMediaType(constants.ERROR_INVALID_FILE)    
    