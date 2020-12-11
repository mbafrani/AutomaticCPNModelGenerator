from flask import Blueprint, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException, BadRequest, NotFound

from util import constants
from services import PetriNetService, EventLogService

JsonKeys = constants.RequestJsonKeys

change_decision_point_page = Blueprint("change_decision_point", __name__)
change_transition_page = Blueprint("change_transition", __name__)


def check_event_log_id(request):
    if not request.json or JsonKeys.event_log_id not in request.json:
        raise BadRequest(constants.ERROR_EVENT_LOG_ID_NOT_FOUND_IN_REQUEST)


def change_parameter(request, check_parameter_fun, update_parameter_fun):
    check_event_log_id(request)
    check_parameter_fun(request)
    event_log_id = request.json["event_log_id"]
    if not EventLogService.is_event_log_id_feasible(event_log_id):
        raise NotFound(constants.ERROR_EVENT_LOG_DOESNT_EXIST)

    petri_net_service = PetriNetService(event_log_id)
    try:
        update_parameter_fun(petri_net_service, event_log_id)

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
    except Exception as exception:  # Todo handle non HTTPExceptions
        print(exception)
        return make_response(jsonify(exception))


@change_transition_page.route("/change-transition", methods=["POST"])
def change_transition():
    def check_parameters(request):
        for element in [JsonKeys.transition, JsonKeys.mean, JsonKeys.std]:
            if element not in request.json:
                raise BadRequest(constants.ERROR_MISSING_PARAMETER_PERFORMANCE)

    def update_parameters(petri_net_service, event_log_id):
        transition = request.json[JsonKeys.transition]
        mean = request.json[JsonKeys.mean]
        std = request.json[JsonKeys.std]
        petri_net_service.update_transition(transition, mean, std)

    return change_parameter(request, check_parameters, update_parameters)


@change_decision_point_page.route("/change-decision-point", methods=["POST"])
def change_decision_point():
    # Todo: Remove this functionality, as it is not in the requirements.
    def check_parameters(request):
        if (
            JsonKeys.place not in request.json
            or JsonKeys.frequencies not in request.json
        ):
            raise BadRequest(message=constants.ERROR_MISSING_PARAMETER_FREQUENCY)

    def update_parameters(petri_net_service, event_log_id):
        place = request.json[JsonKeys.place]
        frequencies = request.json[JsonKeys.frequencies]
        petri_net_service.update_decision_point(place, frequencies)

    return change_parameter(request, check_parameters, update_parameters)
