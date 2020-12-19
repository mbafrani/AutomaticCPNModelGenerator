import pm4py

from api.util import constants


class ProbabilityPlace(pm4py.objects.petri.petrinet.PetriNet.Place):

    def __str__(self):
        return "prob_" + str(self.properties[constants.DICT_KEY_PLACE_PROB_INDEX])
