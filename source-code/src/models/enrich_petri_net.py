from statistics import mean, stdev
from enum import Enum
from pm4py.objects.conversion.log import converter as log_conversion
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.util import exec_utils, xes_constants, constants
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.statistics.variants.log import get as variants_get
from pm4py.visualization.petrinet.util import performance_map
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.visualization.petrinet import visualizer
import pm4py.visualization.petrinet.common.visualize as vis_petrinet


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


class EnrichPetriNet:
    def __init__(self, log=None, net=None, initial_marking=None,
                 final_marking=None, gviz=None):
        self.log = log
        self.net = net
        self.initial_marking = initial_marking
        self.final_marking = final_marking
        self.gviz = gviz

    def get_perf_dict_for_petri_net_decoration(self, stats_dict, activities):
        perf_dict = {}
        for key, value in stats_dict.items():
            transition = key.split("(t)", 1)[1]
            if transition in activities:
                if transition not in perf_dict:
                    perf_dict[transition] = [value]
                else:
                    perf_dict[transition].append(value)

        for key, value in perf_dict.items():
            perf_dict[key] = mean(value)

        return perf_dict

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
            if type(elem) is PetriNet.Arc:
                if statistics[elem]["performance"]:
                    aggr_stat = self.aggregate_stats(statistics, elem,
                                                     aggregation_measure)
                    aggr_stat_hr = round(aggr_stat / 60, 2)
                    aggregated_statistics[str(elem)] = aggr_stat_hr
            elif type(elem) is PetriNet.Place:
                pass
        return aggregated_statistics

    def get_service_time_single_timestamps(self, log, net, initial_marking,
                                           final_marking, parameters=None,
                                           ht_perf_method="last"):
        if parameters is None:
            parameters = {}

        if log is not None:
            log = log_conversion.apply(log, parameters,
                                       log_conversion.TO_EVENT_LOG)
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

            aggregated_statistics \
                = self.get_perf_dict_for_petri_net_decoration(aggregated_statistics,
                                                              list(set(activities)))
            aggregated_statistics_stdev \
                = self.get_perf_dict_for_petri_net_decoration(aggregated_statistics_stdev,
                                                              list(set(activities)))

        return aggregated_statistics, aggregated_statistics_stdev

    def get_service_time_two_timestamps(self, log, parameters=None):
        if parameters is None:
            parameters = {}

        log = log_conversion.apply(log, parameters=parameters)

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

    def enrich_petri_net_perf_info(self):
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

        normalDict = {}
        for key in mean_dict.keys():
            if key in stdev_dict:
                normalDict[key] = ("N(" + str(mean_dict[key]) + ", " +
                                   str(stdev_dict[key]) + ")")

        decorations = {}
        for val in self.net._PetriNet__transitions:
            if str(val) in normalDict.keys():
                label = str(val) + "\n" + normalDict.get(str(val))
                decorations[val] = {"color": "#b3b6b7 ", "label": label}

        parameters = {visualizer.wo_decoration: True}
        self.gviz = vis_petrinet.apply(self.net, self.initial_marking,
                                       self.final_marking,
                                       parameters=parameters,
                                       decorations=decorations)
        return self.gviz
