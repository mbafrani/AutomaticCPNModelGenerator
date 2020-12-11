from flask import Blueprint, request, jsonify, make_response
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError

from util import constants
from services import EventLogService

event_log_page = Blueprint("event_log", __name__)


@event_log_page.route('/event-log', methods=['POST'])
def import_event_log_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return make_response(jsonify(
            message=constants.ERROR_FILE_NOT_FOUND_IN_REQUEST
        ), BadRequest.code)

    file = request.files['file']

    try:
        log_file = EventLogService.save_log_file(file)
        return jsonify(
            message=constants.MESSAGE_EVENT_LOG_UPLOAD_SUCCESS,
            event_log_id=log_file.id
        )
    except HTTPException as exception:
        message = exception.description
        status_code = exception.code
        return make_response(jsonify(
            message=message
        ), status_code)
    except Exception as exp:
        message = exp.args[1]
        return make_response(jsonify(
            message=message
        ), InternalServerError.code)
