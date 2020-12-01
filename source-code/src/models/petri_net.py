import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petrinet import visualizer
import json
import pandas as pd

from util import constants, convert_perf_label_to_seconds

class PetriNet:

  def __init__(self, log=None, net=None, initial_marking=None, final_marking=None, gviz=None):
    self.log = log
    self.net = net
    self.initial_marking = initial_marking
    self.final_marking = final_marking
    self.gviz = gviz

  def import_xes_log(self, file_path):
    self.log = xes_importer.apply(file_path)
    return self.log

  def import_csv_log(self, file_path):
      log_csv = pd.read_csv(file_path)
      log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
      log_csv = log_csv.sort_values('time:timestamp')
      self.log = log_converter.apply(log_csv)
      return self.log

  def discover_process_model(self):
    self.net, self.initial_marking, self.final_marking = inductive_miner.apply(self.log)
    return self.net, self.initial_marking, self.final_marking

  def visualize_process_model(self, enrich_performance=False):
    if (enrich_performance):
      parameters = { 
          visualizer.Variants.WO_DECORATION.value.Parameters.DEBUG: True, 
          visualizer.Variants.PERFORMANCE.value.Parameters.FORMAT: "png" 
      }
      self.gviz = visualizer.apply(
        self.net, 
        self.initial_marking, 
        self.final_marking, 
        parameters=parameters, 
        variant=visualizer.Variants.PERFORMANCE, log=self.log
      )
    else:
      self.gviz = visualizer.apply(
        self.net, 
        self.initial_marking, 
        self.final_marking
      )
    return self.gviz

  def save_petrinet_as_image(self, file_path):
    visualizer.save(self.gviz, file_path)

  # extracts the layout information - x_position, y_position, height and width of graph elements
  # and stores them in the place/transition/arc .properties[LAYOUT_INFORMATION_PETRI]
  # This is needs to be inserted into the cpn file for cpn tools to accurately place the elements in the UI
  def extract_layout_info_to_petri_net_properties(self):
    
    # height and width obtained from graph seems to be in ratios??
    # use the constants to multiply the ratios
    HEIGHT_EXTENSION_CONSTANT = 30
    WIDTH_EXTENSION_CONSTANT = 30

    # decode the Digraph to JSON format
    json_string = self.gviz.pipe('json').decode()
    # parse the resulting json_string
    json_dict = json.loads(json_string)

    # rename source and sink labels in json dictionary
    # source label would be "1" in the dict and sink would be ""
    source_obj = next(
      item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT] if item["label"] == "1"
    )
    source_obj["label"] = "source"
    sink_obj = next(
      item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT] if item["label"] == ""
    )
    sink_obj["label"] = "sink"
    
    # store place's layout information in the properties dictionary
    for place in self.net.places:
        # retreive the place info object from the digraph json dictionary
        obj = next(
          item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT] if item["label"] == str(place)
        )
        pos = obj["pos"].split(',') # the position x and y is a comma seperated string in the dict
        place.properties[constants.LAYOUT_INFORMATION_PETRI] = [
            [ float(pos[0]), float(pos[1]) ],
            [ float(obj["height"]) * HEIGHT_EXTENSION_CONSTANT, float(obj["width"]) * WIDTH_EXTENSION_CONSTANT ]
        ]
    
    # store transition's layout information in the properties dictionary
    for trans in self.net.transitions:
        # retreive the transition info object from the digraph json dictionary
        obj = next(
          item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT] if item["label"] == str(trans)
        )
        pos = obj["pos"].split(',') # the position x and y is a comma seperated string in the dict
        trans.properties[constants.LAYOUT_INFORMATION_PETRI] = [
            [ float(pos[0]), float(pos[1]) ],
            [ float(obj["height"]) * HEIGHT_EXTENSION_CONSTANT, float(obj["width"]) * WIDTH_EXTENSION_CONSTANT ]
        ]
        
    # store arc's layout information for annotations in the properties dictionary
    for item in json_dict[constants.DICT_KEY_EDGES_CONSTANT]:
        source = json_dict["objects"][item["tail"]]
        target = json_dict["objects"][item["head"]]
        # retreive the object with matching source and target label from the petri net arcs
        arc = next(
          arc for arc in self.net.arcs if str(arc.source) == str(source["label"]) and str(arc.target) == str(target["label"])
        )
        pos = item["pos"].split(' ')[3].split(',')
        arc.properties[constants.LAYOUT_INFORMATION_PETRI] = [
            [ float(pos[0]), float(pos[1])]
        ]
        # TODO: Refactor this code
        # store waiting time in the properties dictionary if target is a transition (this is used to induce delay later in cpn)
        # else store the execution time in arc properties (this is used to set exec time later in cpn)
        is_target_trans = isinstance(arc.target, pm4py.objects.petri.petrinet.PetriNet.Transition)
        if (is_target_trans):
            arc.target.properties[constants.PERFORMANCE_INFORMATION_PETRI] = convert_perf_label_to_seconds(item["label"])
        else:
            arc.properties[constants.PERFORMANCE_INFORMATION_PETRI] = convert_perf_label_to_seconds(item["label"])  
