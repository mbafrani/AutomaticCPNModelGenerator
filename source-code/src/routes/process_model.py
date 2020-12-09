from flask import Blueprint, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException, BadRequest

from util import constants
from services import PetriNetService

process_model_page = Blueprint("process_model", __name__)


@process_model_page.route('/process-model', methods=['POST'])
def discover_process_model():
    if not request.json or 'event_log_id' not in request.json:
        return make_response(jsonify(
            message=constants.ERROR_EVENT_LOG_ID_NOT_FOUND_IN_REQUEST
        ), BadRequest.code)

    event_log_id = request.json['event_log_id']

    try:
        petri_net_service = PetriNetService(event_log_id)
        petri_net_service.get_petri_net()
        process_model_file_path = \
            petri_net_service.get_process_model_image_path()
        return send_file(process_model_file_path, as_attachment=True)

    except HTTPException as exception:
        message = exception.description
        status_code = exception.code
        return make_response(jsonify(
            message=message
        ), status_code)
