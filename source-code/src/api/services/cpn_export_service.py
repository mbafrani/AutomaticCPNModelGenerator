import pm4py
from flask import current_app
from xml.dom.minidom import DOMImplementation
import os
import uuid

from api.models import ProbabilityPlace
from api.util import constants


class CPNExportService:

    def __init__(self):
        # this property keep track of equal chance decision probabilities
        self.decision_equal_prob_found = False

    # globbox element in the cpn file contains color set declarations
    def create_globbox_element_for_document(self, document):
        globbox_tag = document.createElement("globbox")

        # setup color set declarations

        # color for case id
        color_tag = document.createElement("color")
        color_tag.setAttribute("id", str(uuid.uuid1().hex))

        colorid_tag = document.createElement("id")
        colorid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_CASE_ID)))
        color_tag.appendChild(colorid_tag)

        colortimed_tag = document.createElement("timed")
        color_tag.appendChild(colortimed_tag)

        colorint_tag = document.createElement(str(constants.DECLARATION_COLOR_CASE_ID_DATATYPE))
        color_tag.appendChild(colorint_tag)

        globbox_tag.appendChild(color_tag)

        # color for probabilty info
        color_tag = document.createElement("color")
        color_tag.setAttribute("id", str(uuid.uuid1().hex))

        colorid_tag = document.createElement("id")
        colorid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_PROBABILITY)))
        color_tag.appendChild(colorid_tag)

        colorint_tag = document.createElement(str(constants.DECLARATION_COLOR_PROBABILITY_DATATYPE))
        color_tag.appendChild(colorint_tag)

        globbox_tag.appendChild(color_tag)

        # setup color set variables declarations

        # case id variable
        var_tag = document.createElement("var")
        var_tag.setAttribute("id", str(uuid.uuid1().hex))

        vartype_tag = document.createElement("type")
        vartypeid_tag = document.createElement("id")
        vartypeid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_CASE_ID)))
        vartype_tag.appendChild(vartypeid_tag)
        var_tag.appendChild(vartype_tag)

        varid_tag = document.createElement("id")
        varid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE)))
        var_tag.appendChild(varid_tag)

        globbox_tag.appendChild(var_tag)

        # probabilty variable
        var_tag = document.createElement("var")
        var_tag.setAttribute("id", str(uuid.uuid1().hex))

        vartype_tag = document.createElement("type")
        vartypeid_tag = document.createElement("id")
        vartypeid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_PROBABILITY)))
        vartype_tag.appendChild(vartypeid_tag)
        var_tag.appendChild(vartype_tag)

        varid_tag = document.createElement("id")
        varid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_PROBABILITY_VARIABLE)))
        var_tag.appendChild(varid_tag)

        globbox_tag.appendChild(var_tag)

        return globbox_tag

    # place element containing place layout information
    def create_place_element_for_page(
     self, place, initial_marking, final_marking, document, is_decision_prob_place=False, is_next_case_id_place=False):
        place_tag = document.createElement("place")
        place_tag.setAttribute("id", str(place.name))

        posattr_tag = document.createElement("posattr")
        posattr_tag.setAttribute(
            "x",
            str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X]
            )
        )
        posattr_tag.setAttribute(
            "y",
            str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_Y]
            )
        )
        place_tag.appendChild(posattr_tag)

        # set fill color for places: Teal(Source), Red(Sink) and
        # White(Others)
        fillattr_tag = document.createElement("fillattr")
        if place in initial_marking.keys():
            fillattr_tag.setAttribute("colour", "Teal")
        elif place in final_marking.keys():
            fillattr_tag.setAttribute("colour", "Red")
        else:
            fillattr_tag.setAttribute("colour", "White")
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        place_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", "Black")
        lineattr_tag.setAttribute("thick", "2")
        lineattr_tag.setAttribute("type", "Solid")
        place_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", "Black")
        textattr_tag.setAttribute("bold", "false")
        place_tag.appendChild(textattr_tag)

        text_tag = document.createElement("text")
        text_tag.appendChild(document.createTextNode(str(place)))
        place_tag.appendChild(text_tag)

        ellipse_tag = document.createElement("ellipse")
        ellipse_tag.setAttribute(
            "h",
            str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_HEIGHT]
            )
        )
        ellipse_tag.setAttribute(
            "w",
            str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_WIDTH]
            )
        )
        place_tag.appendChild(ellipse_tag)

        # TODO: Handle tokens
        token_tag = document.createElement("token")
        token_tag.setAttribute("x", "0.000000")
        token_tag.setAttribute("y", "0.000000")
        place_tag.appendChild(token_tag)

        # TODO: Handle markings
        marking_tag = document.createElement("marking")
        marking_tag.setAttribute("x", "0.000000")
        marking_tag.setAttribute("y", "0.000000")
        place_tag.appendChild(marking_tag)

        type_tag = document.createElement("type")
        type_tag.setAttribute("id", str(uuid.uuid1().hex))

        # color set type for places, setup type tag at bottom-right of the
        # place
        posattr_tag = document.createElement("posattr")
        # attribute position_x = place_position_x + place_width
        posattr_tag.setAttribute("x", str(
            place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
            [constants.DICT_KEY_LAYOUT_X] +
            place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
            [constants.DICT_KEY_LAYOUT_WIDTH]
        ))
        # attribute position_y = place_y_position - place_height/2
        posattr_tag.setAttribute("y", str(
            place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
            [constants.DICT_KEY_LAYOUT_Y] -
            (
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_HEIGHT] / 2
            )
        ))
        type_tag.appendChild(posattr_tag)

        fillattr_tag = document.createElement("fillattr")
        fillattr_tag.setAttribute("colour", "White")
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        type_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", "Black")
        lineattr_tag.setAttribute("thick", "0")
        lineattr_tag.setAttribute("type", "Solid")
        type_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", "Black")
        textattr_tag.setAttribute("bold", "false")
        type_tag.appendChild(textattr_tag)

        text_tag = document.createElement("text")
        if is_next_case_id_place:
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_CASE_ID)))
        elif is_decision_prob_place:
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_PROBABILITY)))  
        else:
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_CASE_ID)))
        type_tag.appendChild(text_tag)

        place_tag.appendChild(type_tag)

        # setup inital markings
        if is_decision_prob_place or is_next_case_id_place:
            initmark_tag = document.createElement("initmark")
            initmark_tag.setAttribute("id", str(uuid.uuid1().hex))

            posattr_tag = document.createElement("posattr")
            # initial_marking position_x = place_x_position + place_width
            posattr_tag.setAttribute("x", str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X] +
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_WIDTH]
            ))
            # initial_marking position_y = place_y_position +
            # place_height/2
            posattr_tag.setAttribute("y", str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_Y] +
                (
                    place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_HEIGHT] / 2
                )
            ))
            initmark_tag.appendChild(posattr_tag)

            fillattr_tag = document.createElement("fillattr")
            fillattr_tag.setAttribute("colour", "White")
            fillattr_tag.setAttribute("pattern", "Solid")
            fillattr_tag.setAttribute("filled", "false")
            initmark_tag.appendChild(fillattr_tag)

            lineattr_tag = document.createElement("lineattr")
            lineattr_tag.setAttribute("colour", "Black")
            lineattr_tag.setAttribute("thick", "0")
            lineattr_tag.setAttribute("type", "Solid")
            initmark_tag.appendChild(lineattr_tag)

            textattr_tag = document.createElement("textattr")
            textattr_tag.setAttribute("colour", "Black")
            textattr_tag.setAttribute("bold", "false")
            initmark_tag.appendChild(textattr_tag)

            text_tag = document.createElement("text")
            if is_next_case_id_place:
                text_tag.appendChild(document.createTextNode(
                    str(1)))
            elif is_decision_prob_place:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_PROBABILITY_FUNCTION)))
            initmark_tag.appendChild(text_tag)

            place_tag.appendChild(initmark_tag)

        if is_decision_prob_place:
            fusioninfo_tag = document.createElement("fusioninfo")
            fusioninfo_tag.setAttribute("id", str(uuid.uuid1().hex))
            fusioninfo_tag.setAttribute("name", str(place))

            posattr_tag = document.createElement("posattr")
            # initial_marking position_x = place_x_position - place_width
            posattr_tag.setAttribute("x", str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X] -
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_WIDTH] / 2
            ))
            # initial_marking position_y = place_y_position -
            # place_height/2
            posattr_tag.setAttribute("y", str(
                place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_Y] -
                (
                    place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_HEIGHT] / 2
                )
            ))
            fusioninfo_tag.appendChild(posattr_tag)

            fillattr_tag = document.createElement("fillattr")
            fillattr_tag.setAttribute("colour", "White")
            fillattr_tag.setAttribute("pattern", "Solid")
            fillattr_tag.setAttribute("filled", "false")
            fusioninfo_tag.appendChild(fillattr_tag)

            lineattr_tag = document.createElement("lineattr")
            lineattr_tag.setAttribute("colour", "Black")
            lineattr_tag.setAttribute("thick", "0")
            lineattr_tag.setAttribute("type", "Solid")
            fusioninfo_tag.appendChild(lineattr_tag)

            textattr_tag = document.createElement("textattr")
            textattr_tag.setAttribute("colour", "Black")
            textattr_tag.setAttribute("bold", "false")
            fusioninfo_tag.appendChild(textattr_tag)

            place_tag.appendChild(fusioninfo_tag)

        return place_tag

    # trans element containg transition layout information
    def create_trans_element_for_page(self, trans, document):
        trans_tag = document.createElement("trans")
        # remove hypens from the guid (or else cpntool will crash)
        trans_tag.setAttribute("id", str(trans.name).replace('-', ''))

        posattr_tag = document.createElement("posattr")
        posattr_tag.setAttribute(
            "x",
            str(
                trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X]
            )
        )
        posattr_tag.setAttribute(
            "y",
            str(
                trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_Y]
            )
        )
        trans_tag.appendChild(posattr_tag)

        fillattr_tag = document.createElement("fillattr")
        fillattr_tag.setAttribute("colour", "Silver")
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        trans_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", "Black")
        lineattr_tag.setAttribute("thick", "2")
        lineattr_tag.setAttribute("type", "Solid")
        trans_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", "Black")
        textattr_tag.setAttribute("bold", "false")
        trans_tag.appendChild(textattr_tag)

        text_tag = document.createElement("text")
        text_tag.appendChild(document.createTextNode(str(trans)))
        trans_tag.appendChild(text_tag)

        box_tag = document.createElement("box")
        box_tag.setAttribute(
            "h",
            str(
                trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_HEIGHT]
            )
        )
        box_tag.setAttribute(
            "w",
            str(
                trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_WIDTH]
            )
        )
        trans_tag.appendChild(box_tag)

        return trans_tag

    # update trans element with guar condition for probabilty condition
    def update_trans_element_with_guard_cond(self, trans, trans_tag, document):
        cond_tag = document.createElement("cond")
        cond_tag.setAttribute("id", str(uuid.uuid1().hex))

        posattr_tag = document.createElement("posattr")
        posattr_tag.setAttribute(
            "x",
            str(
                trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X] - (
                    trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_WIDTH] / 1.5
                )
            )
        )
        posattr_tag.setAttribute(
            "y",
            str(
                trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_Y] + (
                    trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_HEIGHT] / 1.5
                )
            )
        )
        cond_tag.appendChild(posattr_tag)

        fillattr_tag = document.createElement("fillattr")
        fillattr_tag.setAttribute("colour", "White")
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        cond_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", "Black")
        lineattr_tag.setAttribute("thick", "0")
        lineattr_tag.setAttribute("type", "Solid")
        cond_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", "Black")
        textattr_tag.setAttribute("bold", "false")
        cond_tag.appendChild(textattr_tag)

        text_tag = document.createElement("text")
        # TODO: Refactor this code
        guard_cond = ""
        trans_decision_prob = trans.properties[constants.DICT_KEY_PROBA_INFO_PETRI]
        if trans_decision_prob > 50:
            guard_cond = "[p < " + str(trans_decision_prob) + "]"
        elif trans_decision_prob < 50:
            guard_cond = "[p >= " + str(100 - trans_decision_prob) + "]"
        else:
            if self.decision_equal_prob_found:
                guard_cond = "[p < " + str(trans_decision_prob) + "]"
                self.decision_equal_prob_found = False
            else:
                guard_cond = "[p >= " + str(trans_decision_prob) + "]"
                self.decision_equal_prob_found = True
        text_tag.appendChild(document.createTextNode(str(guard_cond)))
        cond_tag.appendChild(text_tag)

        trans_tag.appendChild(cond_tag)

    # arc element containg arc layout information
    def create_arc_element_for_page(
        self, arc, document,
            is_decision_prob_arc=False, is_next_case_id_arc=False, arrival_rate=None, is_init_arc=False):
        # identify the place and transition ends of the arc
        is_target_trans = isinstance(
            arc.target, pm4py.objects.petri.petrinet.PetriNet.Transition)
        is_target_place = isinstance(
            arc.target, pm4py.objects.petri.petrinet.PetriNet.Place)

        # identify orientation of the arc, Place->Trans or Trans->Place
        orientation = constants.PLACE_TO_TRANS_ORIENTATION \
            if is_target_trans else constants.TRANS_TO_PLACE_ORIENTATION

        # remove hypens from the transend_idref (since we removed
        # the same from transition id above)
        # these id's are references to <place> and <transition> tags
        # generated above
        transend_idref = str(
            arc.target.name).replace(
            '-',
            '') if is_target_trans else str(
            arc.source.name).replace(
            '-',
            '')
        placeend_idref = str(
            arc.target.name) if is_target_place else str(
            arc.source.name)

        arc_tag = document.createElement("arc")
        arc_tag.setAttribute("id", str(uuid.uuid1().hex))
        arc_tag.setAttribute("orientation", orientation)

        posattr_tag = document.createElement("posattr")
        posattr_tag.setAttribute("x", "0.000000")
        posattr_tag.setAttribute("y", "0.000000")
        arc_tag.appendChild(posattr_tag)

        fillattr_tag = document.createElement("fillattr")
        fillattr_tag.setAttribute("colour", "White")
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        arc_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", "Black")
        lineattr_tag.setAttribute("thick", "2")
        lineattr_tag.setAttribute("type", "Solid")
        arc_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", "Black")
        textattr_tag.setAttribute("bold", "false")
        arc_tag.appendChild(textattr_tag)

        arrowattr_tag = document.createElement("arrowattr")
        arrowattr_tag.setAttribute("headsize", "1.000000")
        arrowattr_tag.setAttribute("currentcyckle", "2")
        arc_tag.appendChild(arrowattr_tag)

        transend_tag = document.createElement("transend")
        transend_tag.setAttribute("idref", transend_idref)
        arc_tag.appendChild(transend_tag)

        placeend_tag = document.createElement("placeend")
        placeend_tag.setAttribute("idref", placeend_idref)
        arc_tag.appendChild(placeend_tag)

        # TODO: <bendpoint> - do we need this?

        annot_tag = document.createElement("annot")
        annot_tag.setAttribute("id", str(uuid.uuid1().hex))

        posattr_tag = document.createElement("posattr")
        posattr_tag.setAttribute(
            "x",
            str(
                arc.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X]
            )
        )
        # move y position by 5 else the arc annotation will end up lying on
        # the arc
        posattr_tag.setAttribute(
            "y",
            str(
                arc.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_Y] + 5
            )
        )
        annot_tag.appendChild(posattr_tag)

        fillattr_tag = document.createElement("fillattr")
        fillattr_tag.setAttribute("colour", "White")
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        annot_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", "Black")
        lineattr_tag.setAttribute("thick", "0")
        lineattr_tag.setAttribute("type", "Solid")
        annot_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", "Teal")
        textattr_tag.setAttribute("bold", "false")
        annot_tag.appendChild(textattr_tag)

        text_tag = document.createElement("text")

        if is_decision_prob_arc or is_next_case_id_arc:
            if is_decision_prob_arc:
                if(is_target_place):
                    text_tag.appendChild(document.createTextNode(
                        str(constants.DECLARATION_COLOR_PROBABILITY_FUNCTION)
                    ))
                else:
                    text_tag.appendChild(document.createTextNode(
                        str(constants.DECLARATION_COLOR_PROBABILITY_VARIABLE)
                    ))
            elif is_next_case_id_arc:
                if(is_target_place):
                    text_tag.appendChild(document.createTextNode(
                        str(
                            constants.DECLARATION_COLOR_CASE_ID_VARIABLE +
                            "+1 @+round(exponential(" + str(round(1/arrival_rate, 6)) + "))"
                        )
                    ))
                else:
                    text_tag.appendChild(document.createTextNode(
                        str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE)
                    ))
        elif is_init_arc:
            if(is_target_place):
                text_tag.appendChild(document.createTextNode(
                    str(
                        constants.DECLARATION_COLOR_CASE_ID_VARIABLE
                    )
                ))
        else:
            # Show execution time normal distribution
            # on the arc transition->place
            if(is_target_place):
                execution_time_mean = str(
                    arc.source.properties[constants.DICT_KEY_PERF_INFO_PETRI]
                    [constants.DICT_KEY_PERF_MEAN]
                )
                execution_time_stdev = str(
                    arc.source.properties[constants.DICT_KEY_PERF_INFO_PETRI]
                    [constants.DICT_KEY_PERF_STDEV]
                )
                normal_distrib = str(
                    "normal(" +
                    execution_time_mean +
                    "," +
                    execution_time_stdev +
                    ")"
                )
                text_tag.appendChild(document.createTextNode(
                    str(
                        constants.DECLARATION_COLOR_CASE_ID_VARIABLE) +
                    "@+" +
                    str(
                        "round(" +
                        normal_distrib +
                        ")"
                    )
                ))
            else:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE)))

        annot_tag.appendChild(text_tag)
        arc_tag.appendChild(annot_tag)

        return arc_tag

    def get_arcs_with_prob_info(self, petri_net):
        arcs_from_place_to_trans = {}
        for arc in petri_net.arcs:
            if isinstance(arc.source, pm4py.objects.petri.petrinet.PetriNet.Place):
                arcs_from_place_to_trans.setdefault(str(arc.source.name), []).append(arc)

        # find places in arcs that have multiple arcs
        prob_index = 0
        arcs_with_prob = {
            key: value for key, value in arcs_from_place_to_trans.items() if len(value) > 1
        }
        return arcs_with_prob

    # page element in the cpn file contains all the places, transitions and
    # arcs
    def create_page_element_for_document(
            self,
            document,
            petri_net,
            initial_marking,
            final_marking,
            parameters=None):
        # <page>
        page_tag = document.createElement("page")
        page_tag.setAttribute("id", str(uuid.uuid1().hex))

        # <pageattr name="Page"/>
        pageattr_tag = document.createElement("pageattr")
        pageattr_tag.setAttribute("name", "Page")
        page_tag.appendChild(pageattr_tag)

        # <place>, setup for place ellipses
        source_place = None
        for place in petri_net.places:
            place_tag = self.create_place_element_for_page(
                place,
                initial_marking,
                final_marking,
                document
            )
            if str(place) == "source":
                source_place = place
            page_tag.appendChild(place_tag)

        # <trans>, setup for transition rectangles
        trans_dict = {}
        for trans in petri_net.transitions:
            trans_tag = self.create_trans_element_for_page(trans, document)
            trans_dict[str(trans.name)] = trans_tag
            page_tag.appendChild(trans_tag)

        # <arcs>, setup for arcs
        for arc in petri_net.arcs:
            arc_tag = self.create_arc_element_for_page(arc, document)
            page_tag.appendChild(arc_tag)

        # setup 'Init' transition
        init_trans = pm4py.objects.petri.petrinet.PetriNet.Transition(
            "Init",
            "Init",
            None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                        source_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] - 100
                    ),
                    constants.DICT_KEY_LAYOUT_Y: source_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y],
                    constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                    constants.DICT_KEY_LAYOUT_WIDTH: 25
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 0.0,
                    constants.DICT_KEY_PERF_STDEV: 0.0
                }
            }
        )
        init_trans_tag = self.create_trans_element_for_page(init_trans, document)
        page_tag.appendChild(init_trans_tag)
        # create arc from 'Init' to 'source'
        arc_trans_to_place = pm4py.objects.petri.petrinet.PetriNet.Arc(
            init_trans, source_place, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] + 50,
                    constants.DICT_KEY_LAYOUT_Y: init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y],
                }
            }
        )
        arc_trans_to_place_tag = self.create_arc_element_for_page(arc_trans_to_place, document, is_init_arc=True)
        page_tag.appendChild(arc_trans_to_place_tag)

        # setup next case if place and its arcs to 'Init' transition
        # create <place>
        next_case_id_place = pm4py.objects.petri.petrinet.PetriNet.Place(
            "next_CASE_ID", None, None, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X],
                    constants.DICT_KEY_LAYOUT_Y: (
                        init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] + 50
                    ),
                    constants.DICT_KEY_LAYOUT_HEIGHT: 15,
                    constants.DICT_KEY_LAYOUT_WIDTH: 40
                }
            }
        )
        next_case_id_place_tag = self.create_place_element_for_page(next_case_id_place, {}, {}, document, is_next_case_id_place=True)
        page_tag.appendChild(next_case_id_place_tag)
        # create arc_1
        arc_place_to_trans = pm4py.objects.petri.petrinet.PetriNet.Arc(
            next_case_id_place, init_trans, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                        next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] - 5
                    ),
                    constants.DICT_KEY_LAYOUT_Y: (
                        next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] +
                        init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]
                    ) / 2
                }
            }
        )
        arc_place_to_trans_tag = self.create_arc_element_for_page(arc_place_to_trans, document, is_next_case_id_arc=True)
        page_tag.appendChild(arc_place_to_trans_tag)
        # create arc_2
        arc_trans_to_place = pm4py.objects.petri.petrinet.PetriNet.Arc(
            init_trans, next_case_id_place, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                        next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] + 5
                    ),
                    constants.DICT_KEY_LAYOUT_Y: (
                        next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] +
                        init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]
                    ) / 2
                }
            }
        )
        arrival_rate = float(petri_net.properties[constants.PetriNetDictKeys.arrivalrate])
        arc_trans_to_place_tag = self.create_arc_element_for_page(
            arc_trans_to_place, document, is_next_case_id_arc=True, arrival_rate=arrival_rate
        )
        page_tag.appendChild(arc_trans_to_place_tag)

        # setup fusion probability places
        prob_index = 0
        arcs_with_prob = self.get_arcs_with_prob_info(petri_net)
        for key, value in arcs_with_prob.items():
            prob_index = prob_index + 1
            for arc in value:
                # create <place>
                prob_place = ProbabilityPlace(
                    "prob_" + str(arc.target.name).replace('-', ''), None, None, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: arc.target.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X],
                            constants.DICT_KEY_LAYOUT_Y: (
                                arc.target.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] +
                                arc.target.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_HEIGHT] * 2
                            ),
                            constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                            constants.DICT_KEY_LAYOUT_WIDTH: 25
                        },
                        constants.DICT_KEY_PLACE_PROB_INDEX: prob_index
                    }
                )
                place_tag = self.create_place_element_for_page(prob_place, {}, {}, document, is_decision_prob_place=True)
                page_tag.appendChild(place_tag)
                # create arc_1
                arc_place_to_trans = pm4py.objects.petri.petrinet.PetriNet.Arc(
                    prob_place, arc.target, weight=1, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: (
                                prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] - 5
                            ),
                            constants.DICT_KEY_LAYOUT_Y: (
                                prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] +
                                arc.target.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]
                            ) / 2
                        }
                    }
                )
                arc_place_to_trans_tag = self.create_arc_element_for_page(arc_place_to_trans, document, is_decision_prob_arc=True)
                page_tag.appendChild(arc_place_to_trans_tag)
                # create arc_2
                arc_trans_to_place = pm4py.objects.petri.petrinet.PetriNet.Arc(
                    arc.target, prob_place, weight=1, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: (
                                prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] + 5
                            ),
                            constants.DICT_KEY_LAYOUT_Y: (
                                prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] +
                                arc.target.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]
                            ) / 2
                        }
                    }
                )
                arc_trans_to_place_tag = self.create_arc_element_for_page(arc_trans_to_place, document, is_decision_prob_arc=True)
                page_tag.appendChild(arc_trans_to_place_tag)

                # update trans element with guard condition
                self.update_trans_element_with_guard_cond(
                    arc.target, trans_dict[str(arc.target.name)], document
                )

        return page_tag

    # fusion element containg fusion places information
    def create_fusion_element_for_document(self, document, fusion_elements, fusion_name):
        fusion_tag = document.createElement("fusion")
        fusion_tag.setAttribute("id", str(uuid.uuid1().hex))
        fusion_tag.setAttribute("name", str(fusion_name))

        for fusion_element in fusion_elements:
            fusion_elm_tag = document.createElement("fusion_elm")
            fusion_elm_tag.setAttribute("idref", str(fusion_element))
            fusion_tag.appendChild(fusion_elm_tag)

        return fusion_tag

    # Genarates a cpn dom object filled with information from the petri net
    def create_cpn_model_from_petri_net(
            self,
            petri_net,
            initial_marking,
            final_marking,
            parameters=None):

        custom_dom_imp = DOMImplementation()

        # <!DOCTYPE workspaceElements PUBLIC "-//CPN//DTD CPNXML 1.0//EN"
        # "http://www.daimi.au.dk/~cpntools/bin/DTD/2/cpn.dtd">
        doctype = custom_dom_imp.createDocumentType(
            qualifiedName="workspaceElements",
            publicId="-//CPN//DTD CPNXML 1.0//EN",
            systemId="http://www.daimi.au.dk/~cpntools/bin/DTD/2/cpn.dtd",
        )

        document = custom_dom_imp.createDocument(
            None, "workspaceElements", doctype)

        workspaceElements = document.getElementsByTagName("workspaceElements")[
            0]

        # <generator tool="CPN Tools" version="0.1.69.1" format="2"/>
        generator_tag = document.createElement("generator")
        generator_tag.setAttribute("tool", "CPN Tools")
        generator_tag.setAttribute("version", "0.1.69.1")
        generator_tag.setAttribute("format", "2")
        workspaceElements.appendChild(generator_tag)

        # <cpnet>
        cpnet_tag = document.createElement("cpnet")
        workspaceElements.appendChild(cpnet_tag)

        # <globbox>
        globbox_tag = self.create_globbox_element_for_document(document)
        cpnet_tag.appendChild(globbox_tag)

        # <page>
        page_tag = self.create_page_element_for_document(
            document,
            petri_net,
            initial_marking,
            final_marking,
            parameters=None
        )
        cpnet_tag.appendChild(page_tag)

        # <fusion>
        prob_index = 0
        arcs_with_prob = self.get_arcs_with_prob_info(petri_net)
        for key, value in arcs_with_prob.items():
            prob_index = prob_index + 1
            fusion_name = "prob_" + str(prob_index)
            fusion_elements = []
            for arc in value:
                fusion_elements.append("prob_" + str(arc.target.name).replace('-', ''))
            fusion_tag = self.create_fusion_element_for_document(document, fusion_elements, fusion_name)
            cpnet_tag.appendChild(fusion_tag)

        return document

    def get_cpn_file_path(self, event_log_id):
        cpn_file_extension = "cpn"
        cpn_file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            event_log_id,
            current_app.config["CPN_MODEL_DEFAULT_NAME"] +
            "." +
            cpn_file_extension)
        return cpn_file_path

    # export xml as cpn file
    def save_cpn_model(self, model, event_log_id):
        """Saves the cpn model in the xml to a cpn file in \
            the data/event_log_id folder

        Args:
            model (xml.dom.minidom.Document): cpn model as xml document
            event_log_id (str): Unique event log used as folder name to store the cpn file
        """
        cpn_file_path = self.get_cpn_file_path(event_log_id)
        # <?xml version="1.0" encoding="iso-8859-1"?>
        xml_str = model.toprettyxml(encoding="iso-8859-1")
        with open(cpn_file_path, "wb") as file:
            file.write(xml_str)
