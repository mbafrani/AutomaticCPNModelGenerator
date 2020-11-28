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


def get_successor_frequencies(log, net, im, fm, dps):
    # Gather information on the log and net.
    I, _ = get_decisions_table(log, net, im, fm,)

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


def enrich_petrinet_decision_probabilities(log, net, initial_marking, final_marking):
    decision_points = list(get_decision_points_from_net(net))
    successor_frequencies = get_successor_frequencies(
        log, net, initial_marking, final_marking, decision_points
    )

    # Enrich decision points
    for dp in decision_points:
        dp.properties[dict_key] = successor_frequencies[dp.name]

    return net


def get_decision_points_from_net(net):
    decision_point_names = list(get_decision_points(net).keys())
    for decision_point in net.places:
        if decision_point.name in decision_point_names:
            yield decision_point


def viz_petrinet(net, im, fm):
    parameters = {visualizer.Variants.WO_DECORATION.value.Parameters.DEBUG: True}
    gviz = visualizer.apply(net, init_marking, final_marking, parameters=parameters,)
    visualizer.view(gviz)


def viz_enriched(net, im, fm):
    dps = get_decision_points_from_net(net)
    decorations = {}
    for dp in dps:
        freq_dict = dp.properties[dict_key]
        strings = [name + ": " + f"{freq:.2f}" for name, freq in freq_dict.items()]
        label = "\n".join(strings)
        decorations[dp] = {"color": "#b3b6b7 ", "label": label}
    parameters = {visualizer.wo_decoration: True}
    gviz = vis_petrinet.apply(
        net, im, fm, parameters=parameters, decorations=decorations,
    )
    visualizer.view(gviz)


if __name__ == "__main__":
    # log = xes_importer.apply("[cpn_model_gen/input_data/running-example.xes")
    # log = xes_importer.apply("[cpn_model_gen/input_data/ETM_Configuration1.xes")
    # log = xes_importer.apply("cpn_model_gen/input_data/ETM_Configuration2.xes")

    # Discover Net
    log = xes_importer.apply("cpn_model_gen/input_data/interval_event_log.xes")
    net, init_marking, final_marking = inductive_miner.apply(log)
    viz_petrinet(net, init_marking, final_marking)

    # Enrich Net
    enriched_net = enrich_petrinet_decision_probabilities(
        log, net, init_marking, final_marking
    )
    viz_enriched(enriched_net, init_marking, final_marking)

    # Print frequencies
    # for dp in get_decision_points_from_net(net):
    #     print(dp.name)
    #     freq_dict = dp.properties[dict_key]
    #     print(
    #         "\n\t".join(
    #             name + ": " + f"{freq:.2f}" for name, freq in freq_dict.items()
    #         ),
    #     )
