from flask import current_app
from werkzeug.exceptions import NotFound
import os

from util import constants
from models import PetriNet, load_net, EnrichPetriNet
PetriNetDictKeys = constants.PetriNetDictKeys


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

    def is_process_model_available(self, folder):
        files = os.listdir(folder)
        for file in files:
            if file.lower().endswith(".pnml"):
                return True
        return False

    def save_petri_net(self, folder=None):
        if folder is None:
            folder = os.path.join(current_app.config["UPLOAD_FOLDER"], self.event_log_id)
        self.petri_net.save_net(folder)

    def get_petri_net_folder(self):
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], self.event_log_id)
        return folder

    def get_petri_net(self):
        folder = self.get_petri_net_folder()
        if self.is_process_model_available(folder):
            self.petri_net = load_net(folder)
        else:
            self.petri_net = self.discover_process()
            self.save_petri_net(folder=folder)

        return self.petri_net

    def discover_process(self):
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

        net_enricher = EnrichPetriNet(self.petri_net)
        net_enricher.enrich_petri_net()

        self.generate_petrinet_image()
        return self.petri_net

    def generate_petrinet_image(self):
        self.petri_net.visualize_process_model()
        image_file_path = self.get_process_model_image_path()
        self.petri_net.save_petrinet_as_image(image_file_path)
        return image_file_path

    def discover_process_old(self):
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
        self.petri_net.visualize_process_model_old(enrich_performance=True)

        self.generate_petrinet_image()

        return self.petri_net

    def extract_layout_info_to_petri_net_properties(self):
        self.petri_net.extract_layout_info_to_petri_net_properties()
        return self.petri_net

    def update_transition(self, transition_name, mean, std):
        # Load Petri Net
        self.petri_net = self.get_petri_net()
        net = self.petri_net.net

        # Find Transition
        for trans in net.transitions:
            if str(trans) == transition_name:
                transition = trans
                break
        else:  # nobreak
            raise Exception(f"Could not find transition with name '{transition_name}'.")

        # Update Performance Information
        perf_dict = transition.properties[PetriNetDictKeys.performance]
        perf_dict[PetriNetDictKeys.mean] = mean
        perf_dict[PetriNetDictKeys.std] = std

        # Save Petri Net
        self.save_petri_net()

    def update_decision_point(self, place_name, frequencies):
        # Load Petri Net
        self.petri_net = self.get_petri_net()
        net = self.petri_net.net

        # Find Place
        for place in net.places:
            if str(place) == place_name:
                decision_point = place
                break
        else:  # nobreak
            raise Exception(f"Could not find the specified place.")

        # Check if transitions are feasible
        following_transitions = [str(arc.target) for arc in place.out_arcs]
        proposed_transitions = list(frequencies.keys())

        if len(following_transitions) != len(proposed_transitions):
            raise Exception("List of outgoing arcs does not match the petri net.")

        following_transitions.sort()
        proposed_transitions.sort()
        for following, proposed in zip(following_transitions, proposed_transitions):
            if following != proposed:
                raise Exception("List of outgoing arcs does not match the petri net.")

        # Normalize Frequencies to sum = 1
        freq_sum = sum(frequencies.values())
        for freq in frequencies:
            frequencies[freq] /= freq_sum
        
        # Update Probability Information
        decision_point.properties[PetriNetDictKeys.frequencies] = frequencies

        # Save Petri Net
        self.save_petri_net()

