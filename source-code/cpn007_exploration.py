#%% Imports
import os
import sys
import json

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petrinet import visualizer as pn_visualizer

from pm4py.objects.petri.importer import importer as pnml_importer
from pm4py.objects.petri.exporter import exporter as pnml_exporter


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "models"))
from enrich_petri_net import EnrichPetriNet  # noqa: E402


# %%


def mine_petrinet(path):
    # Discover Net
    log = xes_importer.apply(path)
    net, init_marking, final_marking = inductive_miner.apply(log)
    petrinet = EnrichPetriNet(log, net, init_marking, final_marking)
    petrinet.enrich_petri_net()
    return petrinet


path = os.path.join("test", "input_data", "ETM_Configuration1.xes")
if not os.path.exists(path):
    path = os.path.join("source-code", "test", "input_data", "ETM_Configuration1.xes")
petrinet = mine_petrinet(path)
gviz = petrinet.viz_petri_net()
# gviz = pn_visualizer.apply(
#     petrinet.net, petrinet.initial_marking, petrinet.final_marking
# )
pn_visualizer.view(gviz)

#%% Export
net_name = "my_petri_net.pnml"


def export_petri_net(net, im, fm, path):
    pnml_exporter.apply(net, im, path, final_marking=fm)

    property_dict = {}
    property_dict["transitions"] = {str(elm): elm.properties for elm in net.transitions}
    property_dict["places"] = {str(elm): elm.properties for elm in net.places}
    with open(net_name + "_properties.json", "w") as fp:
        json.dump(property_dict, fp)


export_petri_net(
    petrinet.net, petrinet.initial_marking, petrinet.final_marking, net_name,
)
#%% Import


def import_petri_net(path):
    net, initial_marking, final_marking = pnml_importer.apply(net_name)
    with open(path + "_properties.json") as infile:
        property_dict = json.load(infile)

    def update_dict(in_dict, elements):
        for element in elements:
            props = in_dict.get(str(element))
            if props is not None:
                element.properties.update(props)

    update_dict(property_dict["transitions"], net.transitions)
    update_dict(property_dict["places"], net.places)

    petrinet = EnrichPetriNet(None, net, initial_marking, final_marking)
    return petrinet


imported_petrinet = import_petri_net(net_name)
gviz = imported_petrinet.viz_petri_net()
pn_visualizer.view(gviz)


