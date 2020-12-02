from flask import current_app
from werkzeug.exceptions import NotFound
import os

from util import constants
from models import PetriNet


class PetriNetService:

    def __init__(self):
        self.petri_net = PetriNet()

    def get_process_model_image_path(self, event_log_id):
        image_file_extension = "png"
        image_file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            event_log_id,
            current_app.config["PROCESS_MODEL_DEFAULT_NAME"] +
            "." +
            image_file_extension)

        return image_file_path

    def discover_process(self, event_log_id):

        # dynamically check event log file extension (XES or CSV)
        log_file_extension = None
        for filename in os.listdir(
            os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                event_log_id)):
            if filename.endswith("." + constants.XES_EXTENSION):
                log_file_extension = constants.XES_EXTENSION
            elif filename.endswith("." + constants.CSV_EXTENSION):
                log_file_extension = constants.CSV_EXTENSION

        is_event_log_exists = log_file_extension is not None
        if not is_event_log_exists:
            raise NotFound(constants.ERROR_EVENT_LOG_DOESNT_EXIST)

        event_log_file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            event_log_id,
            current_app.config["EVENT_LOG_DEFAULT_NAME"] +
            "." +
            log_file_extension)
        if log_file_extension == constants.XES_EXTENSION:
            self.petri_net.import_xes_log(event_log_file_path)
        elif log_file_extension == constants.CSV_EXTENSION:
            self.petri_net.import_csv_log(event_log_file_path)

        self.petri_net.discover_process_model()
        self.petri_net.visualize_process_model(enrich_performance=True)

        image_file_path = self.get_process_model_image_path(event_log_id)
        self.petri_net.save_petrinet_as_image(image_file_path)

        return self.petri_net

    def extract_layout_info_to_petri_net_properties(self):
        self.petri_net.extract_layout_info_to_petri_net_properties()
        return self.petri_net
