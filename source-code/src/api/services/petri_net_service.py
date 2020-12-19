from flask import current_app
from werkzeug.exceptions import NotFound
import os

from api.util import constants
from api.models import PetriNet, load_net
from werkzeug.exceptions import BadRequest

PetriNetDictKeys = constants.PetriNetDictKeys
RequestJsonKeys = constants.RequestJsonKeys


class PetriNetService:
    def __init__(self, event_log_id):
        self.event_log_id = event_log_id
        self.petri_net = PetriNet()

    def get_process_model_image_path(self):
        image_file_extension = "png"
        image_file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            self.event_log_id,
            current_app.config["PROCESS_MODEL_DEFAULT_NAME"]
            + "."
            + image_file_extension,
        )

        return image_file_path

    def _is_process_model_available(self, folder):
        files = os.listdir(folder)
        for file in files:
            if file.lower().endswith(".pnml"):
                return True
        return False

    def _save_petri_net(self, folder=None):
        if folder is None:
            folder = os.path.join(
                current_app.config["UPLOAD_FOLDER"], self.event_log_id
            )
        self.petri_net.save_net(folder)

    def _get_petri_net_folder(self):
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], self.event_log_id)
        return folder

    def load_petri_net(self):
        folder = self._get_petri_net_folder()
        if self._is_process_model_available(folder):
            self.petri_net = load_net(folder)
        else:
            self.petri_net = self._discover_petri_net()
            self._save_petri_net(folder=folder)

        return self.petri_net

    def _discover_petri_net(self):
        # dynamically check event log file extension (XES or CSV)
        log_file_extension = None
        for filename in os.listdir(
            os.path.join(current_app.config["UPLOAD_FOLDER"], self.event_log_id)
        ):
            if filename.endswith("." + constants.XES_EXTENSION):
                log_file_extension = constants.XES_EXTENSION
            elif filename.endswith("." + constants.CSV_EXTENSION):
                log_file_extension = constants.CSV_EXTENSION

        is_event_log_exists = log_file_extension is not None
        if not is_event_log_exists:
            raise NotFound(constants.ERROR_EVENT_LOG_DOESNT_EXIST)

        event_log_file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            self.event_log_id,
            current_app.config["EVENT_LOG_DEFAULT_NAME"] + "." + log_file_extension,
        )
        if log_file_extension == constants.XES_EXTENSION:
            self.petri_net.import_xes_log(event_log_file_path)
        elif log_file_extension == constants.CSV_EXTENSION:
            self.petri_net.import_csv_log(event_log_file_path)

        self.petri_net.discover_process_model()

        self.generate_petrinet_image()
        return self.petri_net

    def generate_petrinet_image(self):
        self.petri_net.visualize_process_model()
        file_path = self.get_process_model_image_path()
        self.petri_net.save_petrinet_as_image(file_path)

    def extract_layout_info_to_petri_net_properties(self):
        self.petri_net.visualize_process_model()
        self.petri_net.extract_layout_info_to_petri_net_properties()
        return self.petri_net

    def update_arrivalrate(self, arrivalrate):
        self.petri_net = self.load_petri_net()
        self.petri_net.update_arrivalrate(arrivalrate)

    def update_transitions(self, transitions):
        # Read the json and create input for petri net
        trans_names, means, stds = [], [], []

        for transition in transitions:
            trans_name = transition.get(RequestJsonKeys.transition)
            mean = transition.get(RequestJsonKeys.mean)
            std = transition.get(RequestJsonKeys.std)
            if trans_name is None or mean is None or std is None:
                raise BadRequest(constants.ERROR_MISSING_PARAMETER_PERFORMANCE)
            trans_names.append(trans_name)
            means.append(mean)
            stds.append(std)

        # Load Petri Net
        self.petri_net = self.load_petri_net()
        self.petri_net.update_transitions(trans_names, means, stds)

        # Save Petri Net
        self._save_petri_net()

    def generate_enrichment_dict(self):
        self.load_petri_net()
        return self.petri_net.construct_prop_dict_for_saving()
