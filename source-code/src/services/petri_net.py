from flask import current_app
from werkzeug.exceptions import NotFound
import os

from util import constants
from models import PetriNet

class PetriNetService:
  
  def __init__(self):
    self.petri_net = PetriNet()

  def discover_process(self, event_log_id):

    # TODO: check event log file extension dynamically
    xes_file_extension = "xes"
    event_log_file_path = os.path.join(
      current_app.config['UPLOAD_FOLDER'], 
      event_log_id, 
      current_app.config["EVENT_LOG_DEFAULT_NAME"] + "." + xes_file_extension
    )
    is_event_log_exists = os.path.isfile(event_log_file_path)
    if not is_event_log_exists:
      raise NotFound(constants.ERROR_EVENT_LOG_DOESNT_EXIST)

    self.petri_net.import_event_log(event_log_file_path)
    self.petri_net.discover_process_model()
    self.petri_net.visualize_process_model(enrich_performance=True)

    image_file_extension = "png"
    image_file_path = os.path.join(
      current_app.config['UPLOAD_FOLDER'], 
      event_log_id, 
      current_app.config["PROCESS_MODEL_DEFAULT_NAME"] + "." + image_file_extension
    )
    self.petri_net.save_petrinet_as_image(image_file_path)

    return self.petri_net

  def extract_layout_info_to_petri_net_properties(self):
    self.petri_net.extract_layout_info_to_petri_net_properties()
    return self.petri_net
