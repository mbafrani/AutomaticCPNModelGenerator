from flask import Blueprint, request,\
    jsonify, make_response, send_file
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError

from api.util import constants
from api.services import PetriNetService, CPNExportService

cpn_export_page = Blueprint("cpn_export", __name__)


@cpn_export_page.route('/cpn-export', methods=['POST'])
def export_cpn_file():
    if 'event_log_id' not in request.json:
        return make_response(jsonify(
            message=constants.ERROR_EVENT_LOG_ID_NOT_FOUND_IN_REQUEST
        ), BadRequest.code)

    event_log_id = request.json['event_log_id']

    try:
        petri_net_service = PetriNetService(event_log_id)
        petri_net_service.load_petri_net()
        # extract layout information from graphviz to insert
        # into petrinet place/transitions properties
        petri_net = petri_net_service.\
            extract_layout_info_to_petri_net_properties()

        cpn_export_service = CPNExportService()
        cpn_model = cpn_export_service.create_cpn_model_from_petri_net(
            petri_net.net,
            petri_net.initial_marking,
            petri_net.final_marking
        )
        # save the cpn file to uploads/event-log-id/
        cpn_export_service.save_cpn_model(cpn_model, event_log_id)
        cpn_zip_file_path = cpn_export_service.get_cpn_zip_file_path(event_log_id)

        return send_file(cpn_zip_file_path, as_attachment=True)

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
