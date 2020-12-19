from flask import Blueprint, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError

from api.util import constants
from api.services import PetriNetService, EventLogService

process_model_page = Blueprint("process_model", __name__)


@process_model_page.route("/process-model/<string:event_log_id>", methods=["GET"])
def discover_process_model(event_log_id):

    if not EventLogService.is_event_log_id_feasible(event_log_id):
        return make_response(
            jsonify(message=constants.ERROR_EVENT_LOG_DOESNT_EXIST), InternalServerError.code
        )

    try:
        petri_net_service = PetriNetService(event_log_id)
        petri_net_service.load_petri_net()
        process_model_file_path = petri_net_service.get_process_model_image_path()

        return send_file(process_model_file_path, as_attachment=True)

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


@process_model_page.route("/process-model/enrichment-dict", methods=["POST"])
def discover_enrich_dict():

    if not request.json or "event_log_id" not in request.json:
        return make_response(
            jsonify(message=constants.ERROR_EVENT_LOG_DOESNT_EXIST),
            InternalServerError.code
        )

    event_log_id = request.json["event_log_id"]

    try:
        petri_net_service = PetriNetService(event_log_id)
        petri_net_service.load_petri_net()
        prop_dict = petri_net_service.petri_net.construct_prop_dict_for_saving()
        return make_response(prop_dict)

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
