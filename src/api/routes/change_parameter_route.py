from flask import Blueprint, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException, BadRequest, NotFound, InternalServerError
from api.services.petri_net_service import RequestJsonKeys

from api.util import constants
from api.services import PetriNetService, EventLogService

JsonKeys = constants.RequestJsonKeys
PetriNetDictKeys = constants.PetriNetDictKeys

change_parameter_page = Blueprint("change_parameter", __name__)


def check_request_json(request):
    if not request.json or JsonKeys.event_log_id not in request.json:
        raise BadRequest(constants.ERROR_EVENT_LOG_ID_NOT_FOUND_IN_REQUEST)


def update_parameters(petri_net_service):
    transitions = request.json.get(JsonKeys.transitions)
    if transitions is not None:
        petri_net_service.update_transitions(transitions)
    arrivalrate = request.json.get(JsonKeys.arrivalrate)
    if arrivalrate is not None:
        petri_net_service.update_arrivalrate(arrivalrate)


@change_parameter_page.route("/change-parameter", methods=["POST"])
def change_parameter():
    check_request_json(request)

    event_log_id = request.json["event_log_id"]
    if not EventLogService.is_event_log_id_feasible(event_log_id):
        return make_response(
            jsonify(message=constants.ERROR_EVENT_LOG_DOESNT_EXIST), InternalServerError.code
        )

    petri_net_service = PetriNetService(event_log_id)
    try:
        update_parameters(petri_net_service)

        petri_net_service.generate_petrinet_image()
        if request.json.get("test"):
            prop_dict = petri_net_service.petri_net.construct_prop_dict_for_saving()
            return make_response(prop_dict)
        process_model_file_path = petri_net_service.get_process_model_image_path()

        return send_file(process_model_file_path, as_attachment=True)

    except HTTPException as exception:
        message = exception.description
        status_code = exception.code
        return make_response(jsonify(message=message), status_code)
    except Exception as exp:
        message = exp.args[1]
        return make_response(jsonify(message=message), InternalServerError.code)


@change_parameter_page.route("/change-parameter/<string:event_log_id>", methods=["GET"])
def get_parameters(event_log_id):
    if not EventLogService.is_event_log_id_feasible(event_log_id):
        return make_response(
            jsonify(message=constants.ERROR_EVENT_LOG_DOESNT_EXIST), InternalServerError.code
        )
    try:
        petri_net_service = PetriNetService(event_log_id)
        prop_dict = petri_net_service.generate_enrichment_dict()
        result = {JsonKeys.event_log_id: event_log_id,
                  JsonKeys.arrivalrate: prop_dict[PetriNetDictKeys.net].get
                  (PetriNetDictKeys.arrivalrate)}

        transitions = []
        # Filter out silent transitions
        activities = prop_dict[PetriNetDictKeys.net].get(PetriNetDictKeys.transition_names)
        for trans_name, _mean_std_res in prop_dict[PetriNetDictKeys.transitions].items():
            if trans_name in activities:
                mean_std_res = _mean_std_res[PetriNetDictKeys.performance]
                transition = {
                    RequestJsonKeys.transition: trans_name,
                    RequestJsonKeys.mean: mean_std_res[PetriNetDictKeys.mean],
                    RequestJsonKeys.std: mean_std_res[PetriNetDictKeys.std],
                    RequestJsonKeys.res_capacity: mean_std_res[PetriNetDictKeys.res_capacity],
                }
                transitions.append(transition)

        result[JsonKeys.transitions] = transitions

        return make_response(result)

    except HTTPException as exception:
        message = exception.description
        status_code = exception.code
        return make_response(jsonify(message=message), status_code)
    except Exception as exp:
        message = exp.args[1]
        return make_response(jsonify(message=message), InternalServerError.code)
