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
import os
import pm4py.visualization.petrinet.common.visualize as vis_petrinet
from pm4py.algo.enhancement.decision.algorithm import (
    get_decision_points,
    get_decisions_table,
)
import json
import pandas as pd
import math
from statistics import mean, stdev
from enum import Enum
from collections import Counter
from util import constants
from pm4py.objects.petri.importer import importer as pnml_importer
from pm4py.objects.petri.exporter import exporter as pnml_exporter
from pm4py.statistics.traces.log import case_arrival

PetriNetDictKeys = constants.PetriNetDictKeys


class Parameters(Enum):
    ACTIVITY_KEY = pm4py_constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = pm4py_constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = pm4py_constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def get_petri_net_paths(folder, name):
    net_path = os.path.join(folder, name + ".pnml")
    dict_path = os.path.join(folder, name + "_properties.json")
    return net_path, dict_path


def load_net(folder, name="petri_net"):
    net_path, dict_path = get_petri_net_paths(folder, name)

    net, initial_marking, final_marking = pnml_importer.apply(net_path)
    with open(dict_path) as infile:
        property_dict = json.load(infile)

    def update_dict(in_dict, elements):
        for element in elements:
            props = in_dict.get(str(element))
            if props is not None:
                element.properties.update(props)

    net.properties.update(property_dict[PetriNetDictKeys.net])
    update_dict(property_dict[PetriNetDictKeys.transitions], net.transitions)
    update_dict(property_dict[PetriNetDictKeys.places], net.places)
    petrinet = PetriNet(None, net, initial_marking, final_marking)

    return petrinet


class PetriNet:
    def __init__(
        self, log=None, net=None, initial_marking=None, final_marking=None, gviz=None
    ):
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
        log_csv = log_csv.sort_values("time:timestamp")
        self.log = log_converter.apply(log_csv)
        return self.log

    def discover_process_model(self):
        self.net, self.initial_marking, self.final_marking = inductive_miner.apply(
            self.log
        )

        # Enrich petri net with further information
        PetriNetPerformanceEnricher(self).enrich()
        PetriNetDecisionPointEnricher(self).enrich()

        return self.net, self.initial_marking, self.final_marking

    def visualize_process_model(self):
        self.gviz = PetriNetVisualizer(self).visualize_process_model()
        return self.gviz

    def save_petrinet_as_image(self, file_path):
        visualizer.save(self.gviz, file_path)

    def get_decision_points(self):
        decision_point_names = list(get_decision_points(self.net).keys())
        decision_points = [
            dp for dp in self.net.places if dp.name in decision_point_names
        ]
        return decision_points

    def construct_prop_dict_for_saving(self):
        property_dict = {}

        # Add the petri net
        property_dict[PetriNetDictKeys.net] = self.net.properties.copy()

        # Add arrival rate info from the source arc
        for elm in self.net.arcs:
            if str(elm.source) == 'source':
                property_dict[PetriNetDictKeys.arcs] \
                    = {str(elm): elm.properties}
                break

        # Add performance info from the transitions
        property_dict[PetriNetDictKeys.transitions] = {
            str(elm): elm.properties for elm in self.net.transitions
        }

        # Add probability information from the places
        property_dict[PetriNetDictKeys.places] = {
            str(elm): elm.properties for elm in self.net.places
        }

        return property_dict

    def save_net(self, folder, name="petri_net"):
        net_path, dict_path = get_petri_net_paths(folder, name)

        pnml_exporter.apply(
            self.net, self.initial_marking, net_path, final_marking=self.final_marking
        )

        property_dict = self.construct_prop_dict_for_saving()
        with open(dict_path, "w") as fp:
            json.dump(property_dict, fp)

    # extracts the layout information - x_position, y_position, height and
    # width of graph elements and stores them in the
    # place/transition/arc .properties[DICT_KEY_LAYOUT_INFO_PETRI]
    # This is needs to be inserted into the cpn file for cpn tools to
    # accurately place the elements in the UI
    def extract_layout_info_to_petri_net_properties(self):

        # height and width obtained from graph seems to be in ratios??
        # use the constants to multiply the ratios
        HEIGHT_EXTENSION_CONSTANT = 30
        WIDTH_EXTENSION_CONSTANT = 30

        # decode the Digraph to JSON format
        json_string = self.gviz.pipe("json").decode()
        # parse the resulting json_string
        json_dict = json.loads(json_string)

        # rename source and sink labels in json dictionary
        # source label would be "1" in the dict and sink would be ""
        source_obj = next(
            item
            for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
            if item["label"] == "1"
        )
        source_obj["label"] = "source"
        sink_obj = next(
            item
            for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
            if item["label"] == ""
        )
        sink_obj["label"] = "sink"

        # store place's layout information in the properties dictionary
        for place in self.net.places:
            # retreive the place info object from the digraph json dictionary
            obj = next(
                item
                for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
                if item["label"] == str(place)
            )
            # the position x and y is a comma seperated string in the dict
            pos = obj["pos"].split(",")
            place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI] = {
                constants.DICT_KEY_LAYOUT_X: float(pos[0]),
                constants.DICT_KEY_LAYOUT_Y: float(pos[1]),
                constants.DICT_KEY_LAYOUT_HEIGHT: float(obj["height"]) * HEIGHT_EXTENSION_CONSTANT,
                constants.DICT_KEY_LAYOUT_WIDTH: float(obj["width"]) * WIDTH_EXTENSION_CONSTANT,
            }

        # store transition's layout information in the properties dictionary
        for trans in self.net.transitions:
            # retreive the transition info object from the digraph json
            # dictionary
            obj = next(
                item
                for item in json_dict[constants.DICT_KEY_OBJECTS_CONSTANT]
                if item["label"].split("\n")[0] == str(trans)
            )
            # the position x and y is a comma seperated string in the dict
            pos = obj["pos"].split(",")
            trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI] = {
                constants.DICT_KEY_LAYOUT_X: float(pos[0]),
                constants.DICT_KEY_LAYOUT_Y: float(pos[1]),
                constants.DICT_KEY_LAYOUT_HEIGHT: float(obj["height"]) * HEIGHT_EXTENSION_CONSTANT,
                constants.DICT_KEY_LAYOUT_WIDTH: float(obj["width"]) * WIDTH_EXTENSION_CONSTANT,
            }

        # store arc's layout information for annotations in the properties
        # dictionary
        for item in json_dict[constants.DICT_KEY_EDGES_CONSTANT]:
            source = json_dict["objects"][item["tail"]]
            target = json_dict["objects"][item["head"]]
            # retreive the object with matching source and target label from
            # the petri net arcs
            arc = next(
                arc
                for arc in self.net.arcs
                if str(arc.source) == str(source["label"].split("\n")[0]) and str(arc.target) == str(target["label"].split("\n")[0])
            )
            pos = item["pos"].split(" ")[3].split(",")
            arc.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI] = {
                constants.DICT_KEY_LAYOUT_X: float(pos[0]),
                constants.DICT_KEY_LAYOUT_Y: float(pos[1]),
            }

    def update_transitions(self, transitions, means, stds):
        for transition_name, mean, std in zip(transitions, means, stds):
            # Find Transition
            for trans in self.net.transitions:
                if str(trans) == transition_name:
                    transition = trans
                    break
            else:  # nobreak
                raise Exception(
                    f"Could not find transition with name '{transition_name}'."
                )

            # Update Performance Information
            perf_dict = transition.properties[PetriNetDictKeys.performance]
            perf_dict[PetriNetDictKeys.mean] = mean
            perf_dict[PetriNetDictKeys.std] = std

    def update_arrivalrate(self, arrivalrate):
        self.net.properties[PetriNetDictKeys.arrivalrate] = arrivalrate


class PetriNetContainer:
    def __init__(self, petrinet):
        self.petrinet = petrinet
        self.log = petrinet.log
        self.net = petrinet.net
        self.initial_marking = petrinet.initial_marking
        self.final_marking = petrinet.final_marking


class PetriNetVisualizer(PetriNetContainer):
    def visualize_process_model(self):
        dp_decorations = self._get_dp_arc_decorations()
        place_decorations = self._get_place_decorations()
        transition_decoration = self._get_transition_decoration()
        source_arc_decoration = self._get_source_arc_decoration()

        # Order Ensures that the dp decorations do not overwrite the transition decorations.
        decorations = {**dp_decorations, **transition_decoration, **source_arc_decoration,
                       **place_decorations}

        parameters = {visualizer.wo_decoration: True}
        self.gviz = vis_petrinet.apply(
            self.net,
            self.initial_marking,
            self.final_marking,
            parameters=parameters,
            decorations=decorations,
        )

        return self.gviz

    def _get_place_decorations(self):
        decorations = {
            place: {"color": "#FFFFFF", "label": str(place)}
            for place in self.net.places
        }
        return decorations

    def _get_dp_arc_decorations(self):
        decision_points = self.petrinet.get_decision_points()
        decorations = {}
        for dp in decision_points:
            freq_dict = dp.properties[constants.DICT_KEY_FREQUENCY]
            for arc in dp.out_arcs:
                target_frequency = freq_dict.get(arc.target.name)
                if not target_frequency:
                    target_frequency = freq_dict.get(arc.target.label)
                if target_frequency:
                    label = "{:.2%}".format(target_frequency)
                    decorations[arc] = {
                        "color": "#000000",
                        "penwidth": "1",
                        "label": label,
                    }

        return decorations

    def _get_transition_decoration(self):
        decorations = {}
        # add new decorations for transitions with performance distribution
        for transition in self.net.transitions:
            mean_value = transition.properties[constants.DICT_KEY_PERF_INFO_PETRI][
                constants.DICT_KEY_PERF_MEAN
            ]
            std_value = transition.properties[constants.DICT_KEY_PERF_INFO_PETRI][
                constants.DICT_KEY_PERF_STDEV
            ]
            label = str(transition) + "\n" + ("N(" + str(mean_value) + ", " + str(std_value) + ")")
            decorations[transition] = {"color": "#FFFFFF ", "label": label}
        return decorations

    def _get_source_arc_decoration(self):
        decorations = {}
        for arc in self.net.arcs:
            if str(arc.source) == 'source':
                arrival_rate = arc.properties[constants.DICT_KEY_ARRIVAL_INFO_PETRI][
                    constants.DICT_KEY_ARRIVAL_RATE]
                label = "Arrival Rate \n {} minutes".format(arrival_rate)
                decorations[arc] = {
                        "color": "#000000",
                        "penwidth": "1",
                        "label": label,
                    }
                break

        return decorations


class PetriNetPerformanceEnricher(PetriNetContainer):
    def enrich(self):
        if "start_timestamp" in str(self.log):
            mean_dict, stdev_dict = self._get_service_time_two_timestamps(
                self.log,
                parameters={
                    soj_time_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
                    soj_time_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp",
                }
            )
        else:
            mean_dict, stdev_dict = self._get_service_time_single_timestamps(
                self.log, self.net, self.initial_marking, self.final_marking
            )

        # Get the average event log arrival rate
        case_arrival_ratio = case_arrival.get_case_arrival_avg(
            self.log,
            parameters={case_arrival.Parameters.TIMESTAMP_KEY: "time:timestamp"})

        arrival_rate = math.ceil(case_arrival_ratio/60)

        # store transition's perf information in the properties dictionary
        self._extract_perf_info_to_petri_net_properties(mean_dict, stdev_dict, arrival_rate)

    def _aggregate_stats(self, statistics, elem, aggregation_measure):
        aggr_stat = 0
        if aggregation_measure == "mean" or aggregation_measure is None:
            aggr_stat = mean(statistics[elem]["performance"])
        elif aggregation_measure == "stdev":
            if len(statistics[elem]["performance"]) > 1:
                aggr_stat = stdev(statistics[elem]["performance"])
        return aggr_stat

    def _aggregate_statistics(self, statistics, aggregation_measure=None):
        aggregated_statistics = {}
        for elem in statistics.keys():
            if isinstance(elem, pm4py.objects.petri.petrinet.PetriNet.Arc):
                if statistics[elem]["performance"]:
                    aggr_stat = self._aggregate_stats(
                        statistics, elem, aggregation_measure
                    )
                    aggr_stat_hr = round(aggr_stat / 60, 2)
                    aggregated_statistics.setdefault(str(elem.target), []).append(aggr_stat_hr)

            elif isinstance(elem, pm4py.objects.petri.petrinet.PetriNet.Place):
                pass

        for key, value in aggregated_statistics.items():
            aggregated_statistics[key] = mean(value)

        return aggregated_statistics

    def _get_service_time_single_timestamps(
        self,
        log,
        net,
        initial_marking,
        final_marking,
        parameters=None,
        ht_perf_method="last",
    ):
        if parameters is None:
            parameters = {}

        log = log_converter.apply(log, parameters, log_converter.TO_EVENT_LOG)
        act_key = exec_utils.get_param_value(
            Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
        )
        ts_key = exec_utils.get_param_value(
            Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY
        )
        variants_idx = variants_get.get_variants_from_log_trace_idx(
            log, parameters=parameters
        )
        variants = variants_get.convert_variants_trace_idx_to_trace_obj(
            log, variants_idx
        )

        parameters_tr = {
            token_replay.Variants.TOKEN_REPLAY.value.Parameters.ACTIVITY_KEY: act_key,
            token_replay.Variants.TOKEN_REPLAY.value.Parameters.VARIANTS: variants,
        }

        # do the replay
        aligned_traces = token_replay.apply(
            log, net, initial_marking, final_marking, parameters=parameters_tr
        )

        element_statistics = performance_map.single_element_statistics(
            log,
            net,
            initial_marking,
            aligned_traces,
            variants_idx,
            activity_key=act_key,
            timestamp_key=ts_key,
            ht_perf_method=ht_perf_method,
        )
        aggregated_statistics = self._aggregate_statistics(
            element_statistics, aggregation_measure="mean"
        )
        aggregated_statistics_stdev = self._aggregate_statistics(
            element_statistics, aggregation_measure="stdev"
        )

        return aggregated_statistics, aggregated_statistics_stdev

    def _get_service_time_two_timestamps(self, log, parameters=None):
        if parameters is None:
            parameters = {}

        log = log_converter.apply(log, parameters=parameters)

        act_key = exec_utils.get_param_value(
            Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
        )
        start_ts_key = exec_utils.get_param_value(
            Parameters.START_TIMESTAMP_KEY,
            parameters,
            xes_constants.DEFAULT_TIMESTAMP_KEY,
        )
        ts_key = exec_utils.get_param_value(
            Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY
        )

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

    # extracts the perf information - execution time mean and std deviation
    # and stores them in the transition.properties[DICT_KEY_PERF_INFO_PETRI]
    def _extract_perf_info_to_petri_net_properties(self, mean_dict, stdev_dict, arrival_rate):
        for trans in self.net.transitions:
            # insert the perf info into trans properties
            if constants.DICT_KEY_PERF_INFO_PETRI not in trans.properties:
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI] = {}
            if str(trans) in mean_dict and str(trans) in stdev_dict:
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI][
                    constants.DICT_KEY_PERF_MEAN
                ] = mean_dict[str(trans)]
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI][
                    constants.DICT_KEY_PERF_STDEV
                ] = stdev_dict[str(trans)]
            else:
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI][
                    constants.DICT_KEY_PERF_MEAN
                ] = constants.PERF_MEAN_DEFAULT_VALUE
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI][
                    constants.DICT_KEY_PERF_STDEV
                ] = constants.PERF_STDEV_DEFAULT_VALUE

        for arc in self.net.arcs:
            # Insert arrival info into arcs properties
            if str(arc.source) == 'source' \
                    and constants.DICT_KEY_ARRIVAL_INFO_PETRI not in arc.properties:
                arc.properties[constants.DICT_KEY_ARRIVAL_INFO_PETRI] = {}
                arc.properties[constants.DICT_KEY_ARRIVAL_INFO_PETRI][
                    constants.DICT_KEY_ARRIVAL_RATE] = arrival_rate
                break


class PetriNetDecisionPointEnricher(PetriNetContainer):
    def _get_successor_frequencies(self, dps):
        # Gather information on the log and net.
        I, _ = get_decisions_table(
            self.log, self.net, self.initial_marking, self.final_marking
        )

        decision_points_succsessor_frequencies = {}
        for dp in dps:
            # Get names of transitions that directly follow the decision point
            successor_names = [arc.target.name for arc in dp.out_arcs]
            successor_names += [arc.target.label for arc in dp.out_arcs]

            # Get successors to the place from the log and restrict them to the possible transitions
            successors = [el[1] for el in I[dp.name]]
            restricted_successors = [
                succ for succ in successors if succ in successor_names
            ]

            # Calculate Frequencies
            successor_count = Counter(restricted_successors)

            succ_sum = sum(successor_count.values())
            for succ in successor_count:
                successor_count[succ] /= succ_sum

            decision_points_succsessor_frequencies[dp.name] = successor_count

        return decision_points_succsessor_frequencies

    def enrich(self):
        decision_points = self.petrinet.get_decision_points()
        successor_frequencies = self._get_successor_frequencies(decision_points)

        # Enrich decision points
        for dp in decision_points:
            dp.properties[constants.DICT_KEY_FREQUENCY] = successor_frequencies[dp.name]

        # store transition's decision prob information in the properties dictionary
        self._extract_prob_info_to_petri_net_properties(decision_points)

    # extracts the decision prob information
    # and stores them in the transition.properties[DICT_KEY_PROBA_INFO_PETRI]
    def _extract_prob_info_to_petri_net_properties(self, decision_points):
        # TODO: Refactor this code
        for dp in decision_points:
            freq_dict = dp.properties[constants.DICT_KEY_FREQUENCY]
            for arc in dp.out_arcs:
                target_frequency = freq_dict.get(arc.target.name)
                if not target_frequency:
                    target_frequency = freq_dict.get(arc.target.label)
                if target_frequency:
                    arc.target.properties[constants.DICT_KEY_PROBA_INFO_PETRI] = round(
                        target_frequency * 100
                    )
