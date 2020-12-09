import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.util import exec_utils, xes_constants, constants as pm4py_constants
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.statistics.variants.log import get as variants_get
from pm4py.visualization.petrinet.util import performance_map
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.visualization.petrinet import visualizer
import pm4py.visualization.petrinet.common.visualize as vis_petrinet
from pm4py.algo.enhancement.decision.algorithm import (
    get_decision_points,
    get_decisions_table,
)
import json
from statistics import mean, stdev
from enum import Enum
from collections import Counter
from util import constants, convert_perf_label_to_seconds

freq_dict_key = "successor_frequencies"


class Parameters(Enum):
    ACTIVITY_KEY = pm4py_constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = pm4py_constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = pm4py_constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


class PetriNet:

    def __init__(self, log=None, net=None, initial_marking=None,
                 final_marking=None, gviz=None):
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
        self.net, self.initial_marking, self.final_marking\
            = inductive_miner.apply(self.log)
        return self.net, self.initial_marking, self.final_marking

    def visualize_process_model(self):
        if "start_timestamp" in str(self.log):
            mean_dict, stdev_dict \
                = self.get_service_time_two_timestamps(self.log, parameters={
                    soj_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
                    soj_time_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})
        else:
            mean_dict, stdev_dict \
                = self.get_service_time_single_timestamps(self.log, self.net,
                                                          self.initial_marking,
                                                          self.final_marking)

        # Add decision point probabilities
        decision_points = self.enrich_petrinet_decision_probabilities()

        decorations = {}
        # add new decorations for transitions with performance distribution
        for transition in self.net.transitions:
            mean_value = transition.properties[constants.DICT_KEY_PERF_INFO_PETRI][constants.DICT_KEY_PERF_MEAN]
            std_value = transition.properties[constants.DICT_KEY_PERF_INFO_PETRI][constants.DICT_KEY_PERF_STDEV]
            label = str(transition) + "\n" + ("N(" + str(mean_value) + ", " +
                                              str(std_value) + ")")
            decorations[transition] = {"color": "#FFFFFF ", "label": label}

        # add new decorations for transitions with probabilty information
        dp_decorations = self.get_decision_point_arc_decorations(decision_points)
        decorations.update(dp_decorations)

        # keep the existing decoration for places
        for place in self.net.places:
            decorations[place] = {"color": "#b3b6b7 ", "label": str(place)}

        parameters = {visualizer.wo_decoration: True}
        self.gviz = vis_petrinet.apply(self.net, self.initial_marking,
                                       self.final_marking,
                                       parameters=parameters,
                                       decorations=decorations)

        return self.gviz

    def save_petrinet_as_image(self, file_path):
        visualizer.save(self.gviz, file_path)

    def aggregate_stats(self, statistics, elem, aggregation_measure):
        aggr_stat = 0
        if aggregation_measure == "mean" or aggregation_measure is None:
            aggr_stat = mean(statistics[elem]["performance"])
        elif aggregation_measure == "stdev":
            if len(statistics[elem]["performance"]) > 1:
                aggr_stat = stdev(statistics[elem]["performance"])
        return aggr_stat

    def aggregate_statistics(self, statistics, aggregation_measure=None):
        aggregated_statistics = {}
        for elem in statistics.keys():
            if isinstance(
                    elem, pm4py.objects.petri.petrinet.PetriNet.Arc):
                if statistics[elem]["performance"]:
                    aggr_stat = self.aggregate_stats(statistics, elem,
                                                     aggregation_measure)
                    aggr_stat_hr = round(aggr_stat / 60, 2)
                    aggregated_statistics[str(elem)] = aggr_stat_hr

                    # insert the perf info into element properties
                    if constants.DICT_KEY_PERF_INFO_PETRI not in elem.target.properties:
                        elem.target.properties[constants.DICT_KEY_PERF_INFO_PETRI] = {}
                    elem.target.properties[constants.DICT_KEY_PERF_INFO_PETRI][aggregation_measure] = aggr_stat_hr
            elif isinstance(
                    elem, pm4py.objects.petri.petrinet.PetriNet.Place):
                pass
        return aggregated_statistics

    def get_service_time_single_timestamps(self, log, net, initial_marking,
                                           final_marking, parameters=None,
                                           ht_perf_method="last"):
        if parameters is None:
            parameters = {}

        if log is not None:
            log = log_converter.apply(log, parameters,
                                      log_converter.TO_EVENT_LOG)
            act_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY,
                                                 parameters,
                                                 xes_constants.DEFAULT_NAME_KEY)
            ts_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY,
                                                parameters,
                                                xes_constants.DEFAULT_TIMESTAMP_KEY)
            activities = [ev[act_key] for trace in log for ev in trace]

            variants_idx = variants_get.get_variants_from_log_trace_idx(log, parameters=parameters)
            variants = variants_get.convert_variants_trace_idx_to_trace_obj(log, variants_idx)

            parameters_tr = {token_replay.Variants.TOKEN_REPLAY.value.Parameters.ACTIVITY_KEY: act_key,
                             token_replay.Variants.TOKEN_REPLAY.value.Parameters.VARIANTS: variants}

            # do the replay
            aligned_traces = token_replay.apply(log, net, initial_marking,
                                                final_marking,
                                                parameters=parameters_tr)

            element_statistics \
                = performance_map.single_element_statistics(log, net, initial_marking,
                                                            aligned_traces, variants_idx,
                                                            activity_key=act_key,
                                                            timestamp_key=ts_key,
                                                            ht_perf_method=ht_perf_method)
            aggregated_statistics = self.aggregate_statistics(element_statistics,
                                                              aggregation_measure="mean")
            aggregated_statistics_stdev = self.aggregate_statistics(element_statistics,
                                                                    aggregation_measure="stdev")

        return aggregated_statistics, aggregated_statistics_stdev

    def get_service_time_two_timestamps(self, log, parameters=None):
        if parameters is None:
            parameters = {}

        log = log_converter.apply(log, parameters=parameters)

        act_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY,
                                             parameters,
                                             xes_constants.DEFAULT_NAME_KEY)
        start_ts_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY,
                                                  parameters,
                                                  xes_constants.DEFAULT_TIMESTAMP_KEY)
        ts_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                            xes_constants.DEFAULT_TIMESTAMP_KEY)

        durations_dict_mean = {}
        durations_dict_stdev = {}
        activities = [ev[act_key] for trace in log for ev in trace]
        for act in activities:
            durations_dict_mean[act] = []
            durations_dict_stdev[act] = []

        for trace in log:
            for event in trace:
                activity = event[act_key]
                start_time = event[start_ts_key].timestamp()
                complete_time = event[ts_key].timestamp()
                durations_dict_mean[activity].append(complete_time - start_time)
                durations_dict_stdev[activity].append(complete_time - start_time)

        for act in durations_dict_mean:
            durations_dict_mean[act] = round(mean(durations_dict_mean[act]) / 60, 2)

        for act in durations_dict_stdev:
            durations_dict_stdev[act] = round(stdev(durations_dict_stdev[act]) / 60, 2)

        return durations_dict_mean, durations_dict_stdev

    def get_successor_frequencies(self, dps):
        # Gather information on the log and net.
        I, _ = get_decisions_table(self.log, self.net, self.initial_marking, self.final_marking)

        decision_points_succsessor_frequencies = {}
        for dp in dps:
            # Get names of transitions that directly follow the decision point
            successor_names = [arc.target.name for arc in dp.out_arcs]
            successor_names += [arc.target.label for arc in dp.out_arcs]

            # Get successors to the place from the log and restrict them to the possible transitions
            successors = [el[1] for el in I[dp.name]]
            restricted_successors = [succ for succ in successors if succ in successor_names]

            # Calculate Frequencies
            successor_count = Counter(restricted_successors)

            succ_sum = sum(successor_count.values())
            for succ in successor_count:
                successor_count[succ] /= succ_sum

            decision_points_succsessor_frequencies[dp.name] = successor_count

        return decision_points_succsessor_frequencies

    def enrich_petrinet_decision_probabilities(self):
        decision_point_names = list(get_decision_points(self.net).keys())
        decision_points = [dp for dp in self.net.places if dp.name in decision_point_names]

        successor_frequencies = self.get_successor_frequencies(decision_points)

        # Enrich decision points
        for dp in decision_points:
            dp.properties[freq_dict_key] = successor_frequencies[dp.name]
        return decision_points

    def get_decision_point_arc_decorations(self, decision_points):
        decorations = {}
        for dp in decision_points:
            freq_dict = dp.properties[freq_dict_key]
            for arc in dp.out_arcs:
                target_frequency = freq_dict.get(arc.target.name)
                if not target_frequency:
                    target_frequency = freq_dict.get(arc.target.label)
                if target_frequency:
                    label = "{:.2%}".format(target_frequency)
                    decorations[arc] = {"color": "#000000", "penwidth": "1", "label": label}
        return decorations

    # extracts the layout information - x_position, y_position, height and
    # width of graph elements
    # and stores them in the
    # place/transition/arc .properties[DICT_KEY_LAYOUT_INFO_PETRI]
    # This is needs to be inserted into the cpn file for cpn tools to
    # accurately place the elements in the UI
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
            item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
            if item["label"] == "1"
        )
        source_obj["label"] = "source"
        sink_obj = next(
            item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
            if item["label"] == ""
        )
        sink_obj["label"] = "sink"

        # store place's layout information in the properties dictionary
        for place in self.net.places:
            # retreive the place info object from the digraph json dictionary
            obj = next(
                item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
                if item["label"] == str(place)
            )
            # the position x and y is a comma seperated string in the dict
            pos = obj["pos"].split(',')
            place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI] = {
                constants.DICT_KEY_LAYOUT_X: float(pos[0]),
                constants.DICT_KEY_LAYOUT_Y: float(pos[1]),
                constants.DICT_KEY_LAYOUT_HEIGHT: float(obj["height"]) * HEIGHT_EXTENSION_CONSTANT,
                constants.DICT_KEY_LAYOUT_WIDTH: float(obj["width"]) * WIDTH_EXTENSION_CONSTANT
            }

        # store transition's layout information in the properties dictionary
        for trans in self.net.transitions:
            # retreive the transition info object from the digraph json
            # dictionary
            obj = next(
                item for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
                if item["label"].split('\n')[0] == str(trans)
            )
            # the position x and y is a comma seperated string in the dict
            pos = obj["pos"].split(',')
            trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI] = {
                constants.DICT_KEY_LAYOUT_X: float(pos[0]),
                constants.DICT_KEY_LAYOUT_Y: float(pos[1]),
                constants.DICT_KEY_LAYOUT_HEIGHT: float(obj["height"]) * HEIGHT_EXTENSION_CONSTANT,
                constants.DICT_KEY_LAYOUT_WIDTH: float(obj["width"]) * WIDTH_EXTENSION_CONSTANT
            }

        # store arc's layout information for annotations in the properties
        # dictionary
        for item in json_dict[constants.DICT_KEY_EDGES_CONSTANT]:
            source = json_dict["objects"][item["tail"]]
            target = json_dict["objects"][item["head"]]
            # retreive the object with matching source and target label from
            # the petri net arcs
            arc = next(
                arc for arc in self.net.arcs if str(
                    arc.source) == str(
                    source["label"].split('\n')[0]) and str(
                    arc.target) == str(
                    target["label"].split('\n')[0]))
            pos = item["pos"].split(' ')[3].split(',')
            arc.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI] = {
                constants.DICT_KEY_LAYOUT_X: float(pos[0]),
                constants.DICT_KEY_LAYOUT_Y: float(pos[1])
            }
