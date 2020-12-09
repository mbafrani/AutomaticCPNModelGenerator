from flask import Blueprint, request, jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException, BadRequest

from util import constants
from services import PetriNetService


# TODO: Include in Constants
place_key = "place"
frequencies_key = "frequencies"
transition_key = "transition"
mean_key = "mean"
std_key = "std"

chang_parameter_page = Blueprint("change_parameter", __name__)

def check_parameters(request):
    if not request.json or "event_log_id" not in request.json:
        return make_response(
            jsonify(message=constants.ERROR_EVENT_LOG_ID_NOT_FOUND_IN_REQUEST),
            BadRequest.code,
        )
    # Todo: Constant
    if all(element not in request.json for element in [place_key, transition_key]):
        return make_response(jsonify(message="No Transition or transition chosen!"))

    return None


@chang_parameter_page.route("/changeparameter", methods=["POST"])
def change_parameter():
    error_response = check_parameters(request)
    if error_response:
        return error_response

    petri_net_service = PetriNetService()
    event_log_id = request.json["event_log_id"]
    try:
        if place_key in request.json:
            # TODO: How to copy with faulty input? (Activity names that are not allowed, numbers not adding to 1)
            place = request.json[place_key]
            frequencies = request.json[frequencies_key]
            petri_net_service.update_decision_point(event_log_id, place, frequencies)

        elif transition_key in request.json:
            transition = request.json[transition_key]
            mean = request.json[mean_key]
            std = request.json[std_key]
            petri_net_service.update_transition(event_log_id, transition, mean, std)

        # TODO: should I generate a petrinet image evrytime we change a place, or should we do this in bulk?
        petri_net_service.generate_petrinet_image(event_log_id)

        process_model_file_path = petri_net_service.get_process_model_image_path(event_log_id)
        return send_file(process_model_file_path, as_attachment=True)

    except HTTPException as exception:
        message = exception.description
        status_code = exception.code
        return make_response(jsonify(message=message), status_code)
    except Exception as exception: # Todo handle non HTTPExceptions
        return make_response(jsonify(exception))
    
