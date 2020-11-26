from collections import Counter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petrinet import visualizer
from pm4py.algo.enhancement.decision.algorithm import (
    get_decision_points,
    get_decisions_table,
)
import pm4py.visualization.petrinet.common.visualize as vis_petrinet

dict_key = "successor_frequencies"


def get_successor_frequencies(log, net, im, fm, dp_names):
    # Gather information on the log and net.
    I, _ = get_decisions_table(log, net, im, fm,)

    succ_counts = {}
    for dp in dp_names:
        succ_list = [el[1] for el in I[dp]]
        succ_count = Counter(succ_list)
        succ_sum = sum(succ_count.values())
        succ_counts[dp] = {name: count / succ_sum for name, count in succ_count.items()}

    return succ_counts


def enrich_petrinet_prob_dp(log, net, initial_marking, final_marking):
    dp_names = list(get_decision_points(net).keys())
    successor_frequencies = get_successor_frequencies(
        log, net, initial_marking, final_marking, dp_names
    )
    for place in net.places:
        if place.name in dp_names:
            place.properties[dict_key] = successor_frequencies[place.name]

    return net


def viz_petrinet(net, im, fm):
    parameters = {visualizer.Variants.WO_DECORATION.value.Parameters.DEBUG: True}
    gviz = visualizer.apply(net, init_marking, final_marking, parameters=parameters,)
    visualizer.view(gviz)


def viz_enriched(net, im, fm):
    dp_names = list(get_decision_points(net).keys())
    decorations = {}
    for dp in net.places:
        if dp.name not in dp_names:
            continue
        freq_dict = dp.properties[dict_key]
        label = "\n".join(
            name + ": " + f"{freq:.2f}" for name, freq in freq_dict.items()
        )
        decorations[dp] = {"color": "#b3b6b7 ", "label": label}
    parameters = {visualizer.wo_decoration: True}
    gviz = vis_petrinet.apply(
        net, im, fm, parameters=parameters, decorations=decorations,
    )
    visualizer.view(gviz)


if __name__ == "__main__":
    # log = xes_importer.apply("cpn_model_gen/input_data/running-example.xes")
    # log = xes_importer.apply("cpn_model_gen/input_data/ETM_Configuration1.xes")

    # Discover Net
    log = xes_importer.apply("cpn_model_gen/input_data/ETM_Configuration2.xes")
    net, init_marking, final_marking = inductive_miner.apply(log)
    viz_petrinet(net, init_marking, final_marking)

    # Enrich Net
    enriched_net = enrich_petrinet_prob_dp(log, net, init_marking, final_marking)
    viz_enriched(enriched_net, init_marking, final_marking)
