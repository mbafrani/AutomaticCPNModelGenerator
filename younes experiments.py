#%%
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petrinet import visualizer
from pm4py.algo.enhancement.decision import algorithm as decision_mining
from pm4py.algo.filtering.log.attributes import (
    attributes_filter as log_attributes_filter,
)
import pm4py.visualization.petrinet.common.visualize as vis_petrinet

#%% Import XES


log = xes_importer.apply("input_data/running-example.xes")
#%% discover and visualize petri net
net, im, fm = inductive_miner.apply(log)

# Use debug configuration to see the name of added places and skips
parameters = {visualizer.Variants.WO_DECORATION.value.Parameters.DEBUG: True}

gviz = visualizer.apply(net, im, fm, parameters=parameters,)
visualizer.view(gviz)

# %% Find information about decision points
# Decision points are places with more than one outgoing arc
decision_point_names = list(decision_mining.get_decision_points(net).keys())
# Get machine learning data from the log.
decision_frequencies = {}
for dp_name in decision_point_names:
    X, y, targets = decision_mining.apply(log, net, im, fm, decision_point=dp_name)
    prob_info = {}
    succ_counts = y.value_counts()
    succ_probs = succ_counts / sum(succ_counts)
    decision_frequencies[dp_name] = {
        target: succ_probs[i] for i, target in enumerate(targets)
    }
decision_points = [place for place in net.places if place.name in decision_point_names]
# Enrich petri net
for dp in decision_points:
    freq_dict = decision_frequencies[dp.name]
    dp.properties["successor_frequencies"] = freq_dict

gviz_decorations = {}
for dp in decision_points:
    freq_dict = dp.properties["successor_frequencies"]
    label = "\n".join(name + ": " + f"{freq:.2f}" for name, freq in freq_dict.items())

    gviz_decorations[dp] = {"color": "#b3b6b7 ", "label": label}

gviz = vis_petrinet.apply(
    net,
    im,
    fm,
    parameters={visualizer.wo_decoration: True},
    decorations=gviz_decorations,
)
visualizer.view(gviz)
#%%
for dp in decision_points:
    name = dp.name
    # Find information about the decision point
    X, y, class_names = decision_mining.apply(log, net, im, fm, decision_point=name)
    # Mine decision tree:
    clf, feature_names, classes = decision_mining.get_decision_tree(
        log, net, im, fm, decision_point=name
    )
    features = {
        "X": X,
        "y": y,
        "class_names": class_names,
        "clf": clf,
        "feature_names": feature_names,
        "classes": classes,
    }

    # Enrich Petri net by using the properties dictionary.
    dp.properties["decision"] = features

    # Show decision tree
    # gviz = tree_visualizer.apply(clf, feature_names, classes)
    # visualizer.view(gviz)

# %% Performance analysis (Postponed)

# Get Activity names


activities = log_attributes_filter.get_attribute_values(log, "concept:name")
activities = list(activities.keys())
# from pm4py.statistics.performance_spectrum import algorithm as performance_spectrum

# ps = performance_spectrum.apply(
#     log,
#     ["register request", "decide"],
#     parameters={
#         performance_spectrum.Parameters.ACTIVITY_KEY: "concept:name",
#         performance_spectrum.Parameters.TIMESTAMP_KEY: "time:timestamp",
#     },
# )
# ps
