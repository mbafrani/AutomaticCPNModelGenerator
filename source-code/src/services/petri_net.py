from flask import current_app
from werkzeug.exceptions import NotFound
import os

from util import constants
from models import PetriNet, load_net, EnrichPetriNet


# TODO: Constants
freq_dict_key = "successor_frequencies"
performance_dict_key = "performance_information"
mean_dict_key = 'mean'
std_dict_key = 'std'

class PetriNetService:
    def __init__(self):
        self.petri_net = PetriNet()

    def get_process_model_image_path(self, event_log_id): 
        image_file_extension = "png"
        image_file_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            event_log_id,
            current_app.config["PROCESS_MODEL_DEFAULT_NAME"]
            + "."
            + image_file_extension,
        )

        return image_file_path

    def is_process_model_available(self, folder):
        files = os.listdir(folder)
        for file in files:
            if file.lower().endswith(".pnml"):
                return True
        return False

    def save_petri_net(self, event_log_id=None, folder=None):
        if folder is None:
            folder = os.path.join(current_app.config["UPLOAD_FOLDER"], event_log_id)
        self.petri_net.save_net(folder)

    def get_petri_net_folder(self, event_log_id):
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], event_log_id)
        return folder

    def get_petri_net(self, event_log_id):
        folder = self.get_petri_net_folder(event_log_id)
        if self.is_process_model_available(folder):
            self.petri_net = load_net(folder)
        else:
            self.petri_net = self.discover_process(event_log_id)
            self.save_petri_net(folder=folder)

        return self.petri_net

    def discover_process(self, event_log_id):

        # dynamically check event log file extension (XES or CSV)
        log_file_extension = None
        for filename in os.listdir(
            os.path.join(current_app.config["UPLOAD_FOLDER"], event_log_id)
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
            event_log_id,
            current_app.config["EVENT_LOG_DEFAULT_NAME"] + "." + log_file_extension,
        )
        if log_file_extension == constants.XES_EXTENSION:
            self.petri_net.import_xes_log(event_log_file_path)
        elif log_file_extension == constants.CSV_EXTENSION:
            self.petri_net.import_csv_log(event_log_file_path)

        self.petri_net.discover_process_model()

        net_enricher = EnrichPetriNet(self.petri_net)
        net_enricher.enrich_petri_net()

        self.generate_petrinet_image(event_log_id)
        return self.petri_net

    def generate_petrinet_image(self, event_log_id):
        self.petri_net.visualize_process_model()
        image_file_path = self.get_process_model_image_path(event_log_id)
        self.petri_net.save_petrinet_as_image(image_file_path)
        return image_file_path

    def discover_process_old(self, event_log_id):
        # dynamically check event log file extension (XES or CSV)
        log_file_extension = None
        for filename in os.listdir(
            os.path.join(current_app.config["UPLOAD_FOLDER"], event_log_id)
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
            event_log_id,
            current_app.config["EVENT_LOG_DEFAULT_NAME"] + "." + log_file_extension,
        )
        if log_file_extension == constants.XES_EXTENSION:
            self.petri_net.import_xes_log(event_log_file_path)
        elif log_file_extension == constants.CSV_EXTENSION:
            self.petri_net.import_csv_log(event_log_file_path)

        self.petri_net.discover_process_model()
        self.petri_net.visualize_process_model_old(enrich_performance=True)

        self.generate_petrinet_image(event_log_id)

        return self.petri_net

    def extract_layout_info_to_petri_net_properties(self):
        self.petri_net.extract_layout_info_to_petri_net_properties()
        return self.petri_net

    def update_transition(self, event_log_id, transition_name, mean, std):
        # Load Petri Net
        self.petri_net = self.get_petri_net(event_log_id)
        net = self.petri_net.net

        # Find Transition
        transition = next(trans for trans in net.transitions if str(trans) == transition_name)
        if transition is None:
            # TODO: Handle case in higher method
            raise Exception("Could not identify transition")

        # Update Performance Information
        perf_dict = transition.properties[performance_dict_key]
        perf_dict[mean_dict_key] = mean
        perf_dict[std_dict_key] = std

        # Save Petri Net
        self.save_petri_net(event_log_id)

    def update_decision_point(self, event_log_id, place_name, frequencies):
        # Load Petri Net
        self.petri_net = self.get_petri_net(event_log_id)
        net = self.petri_net.net

        # Find Place
        place = next(place for place in net.places if str(place) == place_name)
        if place is None:
            # TODO: Handle case in higher method
            raise Exception("Could not identify place")

        
        # Update Probability Information
        # TODO: Check if the result is feasible
        # Check if the transitions are all present
        # Handle numbers not adding up to 1
        place.properties[freq_dict_key] = frequencies

        # Save Petri Net
        self.save_petri_net(event_log_id)

