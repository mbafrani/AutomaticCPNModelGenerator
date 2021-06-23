import pm4py
from flask import current_app
from xml.dom.minidom import DOMImplementation
import os
import uuid
from zipfile import ZipFile

from api.util import constants


class CPNExportService:

    def __init__(self):
        pass

    # globbox element in the cpn file contains color set declarations
    def create_globbox_element_for_document(self, document, number_of_trans):
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

        # color for resource capacity
        color_tag = document.createElement("color")
        color_tag.setAttribute("id", str(uuid.uuid1().hex))

        colorid_tag = document.createElement("id")
        colorid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_RES_CAPACITY)))
        color_tag.appendChild(colorid_tag)

        colortimed_tag = document.createElement("timed")
        color_tag.appendChild(colortimed_tag)

        enum_tag = document.createElement(str(constants.DECLARATION_COLOR_RES_CAPACITY_DATATYPE))
        enum_id_tag = document.createElement("id")
        enum_id_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE)))
        enum_tag.appendChild(enum_id_tag)
        color_tag.appendChild(enum_tag)

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

        # function declarations
        ml_tag = document.createElement("ml")
        ml_tag.setAttribute("id", str(uuid.uuid1().hex))
        ml_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_NORMAL_DISTRIB_FUNCTION)))
        globbox_tag.appendChild(ml_tag)

        ml_tag = document.createElement("ml")
        ml_tag.setAttribute("id", str(uuid.uuid1().hex))
        ml_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_EXP_DISTRIB_FUNCTION)))
        globbox_tag.appendChild(ml_tag)

        # create block declaration
        block_tag = document.createElement("block")
        block_tag.setAttribute("id", str(uuid.uuid1().hex))
        blockid_tag = document.createElement("id")
        blockid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_BLOCK_EXEC_TIME_ID)))
        block_tag.appendChild(blockid_tag)

        # exec time variable declarations
        for index in range(0, number_of_trans):
            ml_tag = document.createElement("ml")
            ml_tag.setAttribute("id", str(uuid.uuid1().hex))
            ml_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_ASSIGNMENT_EXEC_TIME).format(index)
            ))
            block_tag.appendChild(ml_tag)
        globbox_tag.appendChild(block_tag)

        # use sml file declaration
        use_tag = document.createElement("use")
        use_tag.setAttribute("id", str(uuid.uuid1().hex))
        ml_tag = document.createElement("ml")
        sml_file = current_app.config["SML_FILE_DEFAULT_NAME"] + ".sml"
        ml_tag.appendChild(document.createTextNode(f"\"{sml_file}\""))
        use_tag.appendChild(ml_tag)
        layout_tag = document.createElement("layout")
        layout_tag.appendChild(document.createTextNode(f"use \"{sml_file}\";"))
        use_tag.appendChild(layout_tag)
        globbox_tag.appendChild(use_tag)

        return globbox_tag

    # place element containing place layout information
    def create_place_element_for_page(
            self, place, initial_marking, final_marking, document,
            is_decision_prob_place=False, is_next_case_id_place=False, is_res_cap_place=False, res_capacity=None,
            is_openEL_place=False):
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

        fillattr_tag = document.createElement("fillattr")
        lineattr_tag = document.createElement("lineattr")
        textattr_tag = document.createElement("textattr")

        # set fill/line/text color for places
        if place in initial_marking.keys():
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_SOURCE_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_SOURCE_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_SOURCE_TEXT_COLOR)
        elif place in final_marking.keys():
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_SINK_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_SINK_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_SINK_TEXT_COLOR)
        elif is_decision_prob_place:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DECISION_PROB_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DECISION_PROB_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DECISION_PROB_TEXT_COLOR)
        elif is_next_case_id_place:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_NEXT_CASE_ID_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_NEXT_CASE_ID_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_NEXT_CASE_ID_TEXT_COLOR)
        elif is_res_cap_place:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_RES_CAP_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_RES_CAP_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_RES_CAP_TEXT_COLOR)
        elif is_openEL_place:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_OPEN_EL_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_OPEN_EL_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_OPEN_EL_TEXT_COLOR)
        else:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DEFAULT_FILL_COLOR)
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DEFAULT_LINE_COLOR)
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DEFAULT_TEXT_COLOR)

        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        place_tag.appendChild(fillattr_tag)

        lineattr_tag.setAttribute("thick", "2")
        lineattr_tag.setAttribute("type", "Solid")
        place_tag.appendChild(lineattr_tag)

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

        token_tag = document.createElement("token")
        token_tag.setAttribute("x", "0.000000")
        token_tag.setAttribute("y", "0.000000")
        place_tag.appendChild(token_tag)

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
        textattr_tag.setAttribute("bold", "false")

        text_tag = document.createElement("text")
        if is_next_case_id_place:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_NEXT_CASE_ID_TEXT_COLOR)
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_CASE_ID)))
        elif is_openEL_place:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_OPEN_EL_LINE_COLOR)
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_OPEN_EL_TYPE)))
        elif is_decision_prob_place:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DECISION_PROB_TEXT_COLOR)
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_PROBABILITY)))
        elif is_res_cap_place:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_RES_CAP_TEXT_COLOR)
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_RES_CAPACITY)))
        else:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DEFAULT_TEXT_COLOR)
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_CASE_ID)))

        type_tag.appendChild(textattr_tag)
        type_tag.appendChild(text_tag)

        place_tag.appendChild(type_tag)

        # setup inital markings
        if is_decision_prob_place or is_openEL_place or is_res_cap_place:
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
            textattr_tag.setAttribute("bold", "false")

            text_tag = document.createElement("text")
            if is_openEL_place:
                textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_OPEN_EL_LINE_COLOR)
                text_tag.appendChild(document.createTextNode(
                    str(1)))
            elif is_decision_prob_place:
                textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_DECISION_PROB_TEXT_COLOR)
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_PROBABILITY_FUNCTION)))
            elif is_res_cap_place:
                textattr_tag.setAttribute("colour", constants.CPN_MODEL_PLACE_RES_CAP_TEXT_COLOR)
                text_tag.appendChild(document.createTextNode(
                    str(res_capacity) +
                    "`" +
                    str(constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE)
                ))

            initmark_tag.appendChild(textattr_tag)
            initmark_tag.appendChild(text_tag)

            place_tag.appendChild(initmark_tag)

        return place_tag

    # trans element containg transition layout information
    def create_trans_element_for_page(self, trans, document, non_silent_trans, group_name, is_init_trans=False, is_openfile_trans=False):
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
        if is_openfile_trans:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_TRANS_OPEN_FILE_FILL_COLOR)
        else:
            fillattr_tag.setAttribute("colour", constants.CPN_MODEL_TRANS_DEFAULT_FILL_COLOR)
        fillattr_tag.setAttribute("pattern", "Solid")
        fillattr_tag.setAttribute("filled", "false")
        trans_tag.appendChild(fillattr_tag)

        lineattr_tag = document.createElement("lineattr")
        lineattr_tag.setAttribute("colour", constants.CPN_MODEL_TRANS_DEFAULT_LINE_COLOR)
        lineattr_tag.setAttribute("thick", "2")
        lineattr_tag.setAttribute("type", "Solid")
        trans_tag.appendChild(lineattr_tag)

        textattr_tag = document.createElement("textattr")
        textattr_tag.setAttribute("colour", constants.CPN_MODEL_TRANS_DEFAULT_TEXT_COLOR)
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

        # code segment for open_file trans
        if is_openfile_trans:
            code_tag = document.createElement("code")
            code_tag.setAttribute("id", str(uuid.uuid1().hex))

            posattr_tag = document.createElement("posattr")
            posattr_tag.setAttribute(
                "x",
                str(
                    trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] +
                    (
                            trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH] + 15
                    )
                )
            )
            posattr_tag.setAttribute(
                "y",
                str(
                    trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] -
                    (
                            trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_HEIGHT] / 1.2
                    ) - 2
                )
            )
            code_tag.appendChild(posattr_tag)

            fillattr_tag = document.createElement("fillattr")
            fillattr_tag.setAttribute("colour", "White")
            fillattr_tag.setAttribute("pattern", "Solid")
            fillattr_tag.setAttribute("filled", "false")
            code_tag.appendChild(fillattr_tag)

            lineattr_tag = document.createElement("lineattr")
            lineattr_tag.setAttribute("colour", "Black")
            lineattr_tag.setAttribute("thick", "0")
            lineattr_tag.setAttribute("type", "Solid")
            code_tag.appendChild(lineattr_tag)

            textattr_tag = document.createElement("textattr")
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_TRANS_DEFAULT_TEXT_COLOR)
            textattr_tag.setAttribute("bold", "false")
            code_tag.appendChild(textattr_tag)

            text_tag = document.createElement("text")
            text_tag.appendChild(document.createTextNode(constants.DECLARATION_CODE_SEGMENT_OPEN_FILE))
            code_tag.appendChild(text_tag)

            trans_tag.appendChild(code_tag)

        # code segment for setting the exec time distribution
        if not is_init_trans:
            code_tag = document.createElement("code")
            code_tag.setAttribute("id", str(uuid.uuid1().hex))

            posattr_tag = document.createElement("posattr")
            posattr_tag.setAttribute(
                "x",
                str(
                    trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] +
                    (
                            trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH] + 15
                    )
                )
            )
            posattr_tag.setAttribute(
                "y",
                str(
                    trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] -
                    (
                            trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_HEIGHT] / 1.2
                    ) - 2
                )
            )
            code_tag.appendChild(posattr_tag)

            fillattr_tag = document.createElement("fillattr")
            fillattr_tag.setAttribute("colour", "White")
            fillattr_tag.setAttribute("pattern", "Solid")
            fillattr_tag.setAttribute("filled", "false")
            code_tag.appendChild(fillattr_tag)

            lineattr_tag = document.createElement("lineattr")
            lineattr_tag.setAttribute("colour", "Black")
            lineattr_tag.setAttribute("thick", "0")
            lineattr_tag.setAttribute("type", "Solid")
            code_tag.appendChild(lineattr_tag)

            textattr_tag = document.createElement("textattr")
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_TRANS_DEFAULT_TEXT_COLOR)
            textattr_tag.setAttribute("bold", "false")
            code_tag.appendChild(textattr_tag)

            exec_time_mean = str(
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI]
                [constants.DICT_KEY_PERF_MEAN]
            )
            exec_time_stdev = str(
                trans.properties[constants.DICT_KEY_PERF_INFO_PETRI]
                [constants.DICT_KEY_PERF_STDEV]
            )
            normal_distrib = "N(" + exec_time_mean + ", " + exec_time_stdev + ")"

            if str(trans) in non_silent_trans:
                text_tag = document.createElement("text")
                text_tag.appendChild(document.createTextNode(
                    constants.DECLARATION_CODE_SEGMENT_INPUT + "\n" +
                    str(constants.DECLARATION_CODE_SEGMENT_ACTION).format(
                        constants.DECLARATION_VAR_EXEC_TIME.format(
                            trans.properties[constants.DICT_KEY_TRANS_INDEX_PETRI]),
                        str(trans),
                        group_name,
                        normal_distrib
                    )
                ))
                code_tag.appendChild(text_tag)

            trans_tag.appendChild(code_tag)

        return trans_tag

    # update trans element with guar condition for probabilty condition
    def update_trans_element_with_guard_cond(self, trans, trans_tag, document, probs_of_source_place):
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
        trans_prob_index = probs_of_source_place.index(
            (trans.name, trans_decision_prob)
        )

        if trans_prob_index == 0:  # the highest probabilty transition
            guard_cond = "[p < " + str(trans_decision_prob) + "]"
        elif trans_prob_index == (len(probs_of_source_place) - 1):  # the lowest probabilty transition
            guard_cond = "[p >= " + str(100 - trans_decision_prob) + "]"
        else:  # everything in between
            prev_acc_sum = sum([tup[1] for tup in probs_of_source_place[:trans_prob_index]])
            next_acc_sum = sum([tup[1] for tup in probs_of_source_place[(trans_prob_index + 1):]])
            guard_cond = "[p >= " + str(prev_acc_sum) + " andalso p < " + str(100 - next_acc_sum) + "]"

        text_tag.appendChild(document.createTextNode(str(guard_cond)))
        cond_tag.appendChild(text_tag)

        trans_tag.appendChild(cond_tag)

    # arc element containg arc layout information
    def create_arc_element_for_page(
            self, arc, document,
            is_decision_prob_arc=False, is_next_case_id_arc=False, arrival_rate=None, is_init_arc=False,
            is_res_cap_arc=False, is_openEL_arc=False):
        # identify the place and transition ends of the arc
        is_target_trans = isinstance(
            arc.target, pm4py.objects.petri_net.obj.PetriNet.Transition)
        is_target_place = isinstance(
            arc.target, pm4py.objects.petri_net.obj.PetriNet.Place)

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
        if is_next_case_id_arc:
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_NEXT_CASE_ID_LINE_COLOR)
        elif is_decision_prob_arc:
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_DECISION_PROB_ANNOT_TEXT_COLOR)
        elif is_res_cap_arc:
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_RES_CAP_ANNOT_TEXT_COLOR)
        else:
            lineattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_DEFAULT_LINE_COLOR)
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

        annot_tag = document.createElement("annot")
        annot_tag.setAttribute("id", str(uuid.uuid1().hex))

        posattr_tag = document.createElement("posattr")
        posattr_tag.setAttribute(
            "x",
            str(
                arc.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                [constants.DICT_KEY_LAYOUT_X] + (
                    18 if is_next_case_id_arc and is_target_place else 0
                )
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
        textattr_tag.setAttribute("bold", "false")

        text_tag = document.createElement("text")

        if is_next_case_id_arc:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_NEXT_CASE_ID_ANNOT_TEXT_COLOR)
            if is_target_place:
                # smooting value to prevent divide by zero error
                if arrival_rate == 0:
                    arrival_rate = 0.0001

                text_tag.appendChild(document.createTextNode(
                    str(
                        constants.DECLARATION_COLOR_CASE_ID_VARIABLE +
                        "+1@+round(norm_r_at_delay(" + str(arrival_rate) + "))"
                    )
                ))
            else:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE)
                ))
        elif is_init_arc:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_DEFAULT_ANNOT_TEXT_COLOR)
            if is_target_place:
                text_tag.appendChild(document.createTextNode(
                    str(
                        constants.DECLARATION_COLOR_CASE_ID_VARIABLE
                    )
                ))
        elif is_openEL_arc:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_DEFAULT_LINE_COLOR)
            text_tag.appendChild(document.createTextNode(
                str(
                    constants.DECLARATION_COLOR_CASE_ID_VARIABLE
                )
            ))
        elif is_decision_prob_arc:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_DECISION_PROB_ANNOT_TEXT_COLOR)
            if is_target_place:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_PROBABILITY_FUNCTION)
                ))
            else:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_PROBABILITY_VARIABLE)
                ))
        elif is_res_cap_arc:
            # Show execution time normal distribution
            # on the arc transition->place
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_RES_CAP_ANNOT_TEXT_COLOR)
            if is_target_place:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE) +
                    "@+(!" +
                    str(constants.DECLARATION_VAR_EXEC_TIME).format(
                        arc.source.properties[constants.DICT_KEY_TRANS_INDEX_PETRI]
                    ) +
                    ")"
                ))
            else:
                text_tag.appendChild(document.createTextNode(
                    str(
                        constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE
                    )
                ))
        else:
            textattr_tag.setAttribute("colour", constants.CPN_MODEL_ARC_DEFAULT_ANNOT_TEXT_COLOR)
            # Show execution time normal distribution
            # on the arc transition->place
            if is_target_place:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE) +
                    "@+(!" +
                    str(constants.DECLARATION_VAR_EXEC_TIME).format(
                        arc.source.properties[constants.DICT_KEY_TRANS_INDEX_PETRI]
                    ) +
                    ")"
                ))
            else:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE)))

        annot_tag.appendChild(textattr_tag)
        annot_tag.appendChild(text_tag)
        arc_tag.appendChild(annot_tag)

        return arc_tag

    def get_arcs_with_prob_info(self, petri_net):
        arcs_from_place_to_trans = {}
        for arc in petri_net.arcs:
            if isinstance(arc.source, pm4py.objects.petri_net.obj.PetriNet.Place) and \
                    arc.source.name != constants.PLACE_NAME_SOURCE:
                arcs_from_place_to_trans.setdefault(str(arc.source.name), []).append(arc)

        # find places in arcs that have multiple arcs
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
        group_name = ""
        resource_groups = petri_net.properties[constants.DICT_KEY_RESOURCE_POOLING]
        non_silent_trans = petri_net.properties[constants.DICT_KEY_TRANS_NAMES]
        for index, trans in enumerate(petri_net.transitions):
            # store the transition index
            for name, group in resource_groups.items():
                res_activities = group[constants.DICT_KEY_RESOURCE_TRANS]
                if str(trans) in res_activities:
                    group_name = name
                    break
            trans.properties[constants.DICT_KEY_TRANS_INDEX_PETRI] = index
            trans_tag = self.create_trans_element_for_page(trans, document, non_silent_trans, group_name)
            trans_dict[str(trans.name)] = trans_tag
            page_tag.appendChild(trans_tag)

        # adding resource pooling places
        for name, group in resource_groups.items():
            transitions = petri_net.transitions
            trans_group, trans_group_x, trans_group_y = [], [], []
            for trans in transitions:
                if trans.label in group[constants.DICT_KEY_RESOURCE_TRANS]:
                    trans_group.append(trans)
                    trans_group_x.append(
                        trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X])
                    trans_group_y.append(
                        trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y])

            res_capacity_place = pm4py.objects.petri_net.obj.PetriNet.Place(
                name, None, None, properties={
                    constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                        constants.DICT_KEY_LAYOUT_X: trans_group_x[0] - 50,
                        constants.DICT_KEY_LAYOUT_Y: trans_group_y[0] - 30,
                        constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                        constants.DICT_KEY_LAYOUT_WIDTH: 30
                    }
                }
            )
            place_tag = self.create_place_element_for_page(
                res_capacity_place, {}, {}, document, is_res_cap_place=True,
                res_capacity=group[constants.DICT_KEY_RESOURCE_CAP]
            )
            page_tag.appendChild(place_tag)

            for trans in trans_group:
                # create arcs from resource capacity <place> to transition
                arc_place_to_trans = pm4py.objects.petri_net.obj.PetriNet.Arc(
                    res_capacity_place, trans, weight=1, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: (
                                                                 trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                     constants.DICT_KEY_LAYOUT_X] +
                                                                 res_capacity_place.properties[
                                                                     constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                     constants.DICT_KEY_LAYOUT_X]
                                                         ) / 2,
                            constants.DICT_KEY_LAYOUT_Y: ((
                                                                  trans.properties[
                                                                      constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                      constants.DICT_KEY_LAYOUT_Y] +
                                                                  res_capacity_place.properties[
                                                                      constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                      constants.DICT_KEY_LAYOUT_Y]
                                                          ) / 2) - 10
                        }
                    }
                )
                arc_place_to_trans_tag = self.create_arc_element_for_page(arc_place_to_trans, document,
                                                                          is_res_cap_arc=True)
                page_tag.appendChild(arc_place_to_trans_tag)

                # create arc from transition to resource capacity <place>
                arc_trans_to_place = pm4py.objects.petri_net.obj.PetriNet.Arc(
                    trans, res_capacity_place, weight=1, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: ((
                                                                  res_capacity_place.properties[
                                                                      constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                      constants.DICT_KEY_LAYOUT_X] +
                                                                  trans.properties[
                                                                      constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                      constants.DICT_KEY_LAYOUT_X]
                                                          ) / 2) - 30,
                            constants.DICT_KEY_LAYOUT_Y: ((
                                                                  res_capacity_place.properties[
                                                                      constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                      constants.DICT_KEY_LAYOUT_Y] +
                                                                  trans.properties[
                                                                      constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                      constants.DICT_KEY_LAYOUT_Y]
                                                          ) / 2) - 5
                        }
                    }
                )
                arc_trans_to_place_tag = self.create_arc_element_for_page(arc_trans_to_place, document,
                                                                          is_res_cap_arc=True)
                page_tag.appendChild(arc_trans_to_place_tag)

        # <arcs>, setup for arcs
        for arc in petri_net.arcs:
            arc_tag = self.create_arc_element_for_page(arc, document)
            page_tag.appendChild(arc_tag)

        # setup 'Init' <trans>
        init_trans = pm4py.objects.petri_net.obj.PetriNet.Transition(
            "Init",
            "Init",
            None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                            source_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_X] - 100
                    ),
                    constants.DICT_KEY_LAYOUT_Y: source_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                        constants.DICT_KEY_LAYOUT_Y],
                    constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                    constants.DICT_KEY_LAYOUT_WIDTH: 25
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 0.0,
                    constants.DICT_KEY_PERF_STDEV: 0.0
                }
            }
        )
        init_trans_tag = self.create_trans_element_for_page(init_trans, document, non_silent_trans, group_name,
                                                            is_init_trans=True)
        page_tag.appendChild(init_trans_tag)
        # create <arc> from 'Init' to 'source'
        arc_trans_to_place = pm4py.objects.petri_net.obj.PetriNet.Arc(
            init_trans, source_place, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                     constants.DICT_KEY_LAYOUT_X] + 50,
                    constants.DICT_KEY_LAYOUT_Y: init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                        constants.DICT_KEY_LAYOUT_Y],
                }
            }
        )
        arc_trans_to_place_tag = self.create_arc_element_for_page(arc_trans_to_place, document, is_init_arc=True)
        page_tag.appendChild(arc_trans_to_place_tag)

        # setup next case if place and its arcs to 'Init' transition
        # create <place>
        next_case_id_place = pm4py.objects.petri_net.obj.PetriNet.Place(
            "next_CASE_ID", None, None, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                        constants.DICT_KEY_LAYOUT_X],
                    constants.DICT_KEY_LAYOUT_Y: (
                            init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_Y] + 50
                    ),
                    constants.DICT_KEY_LAYOUT_HEIGHT: 15,
                    constants.DICT_KEY_LAYOUT_WIDTH: 40
                }
            }
        )
        next_case_id_place_tag = self.create_place_element_for_page(next_case_id_place, {}, {}, document,
                                                                    is_next_case_id_place=True)
        page_tag.appendChild(next_case_id_place_tag)
        # create arc_1
        arc_place_to_trans = pm4py.objects.petri_net.obj.PetriNet.Arc(
            next_case_id_place, init_trans, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                            next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_X] - 5
                    ),
                    constants.DICT_KEY_LAYOUT_Y: (
                                                         next_case_id_place.properties[
                                                             constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                             constants.DICT_KEY_LAYOUT_Y] +
                                                         init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                             constants.DICT_KEY_LAYOUT_Y]
                                                 ) / 2
                }
            }
        )
        arc_place_to_trans_tag = self.create_arc_element_for_page(arc_place_to_trans, document,
                                                                  is_next_case_id_arc=True)
        page_tag.appendChild(arc_place_to_trans_tag)
        # create arc_2
        arc_trans_to_place = pm4py.objects.petri_net.obj.PetriNet.Arc(
            init_trans, next_case_id_place, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                            next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_X] + 5
                    ),
                    constants.DICT_KEY_LAYOUT_Y: (
                                                         next_case_id_place.properties[
                                                             constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                             constants.DICT_KEY_LAYOUT_Y] +
                                                         init_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                             constants.DICT_KEY_LAYOUT_Y]
                                                 ) / 2
                }
            }
        )

        arrival_rate = float(petri_net.properties[constants.PetriNetDictKeys.arrivalrate])
        arc_trans_to_place_tag = self.create_arc_element_for_page(
            arc_trans_to_place, document, is_next_case_id_arc=True, arrival_rate=arrival_rate
        )
        page_tag.appendChild(arc_trans_to_place_tag)

        # ------------------------------------------
        # setup 'Openfile' <trans>
        openfile_trans = pm4py.objects.petri_net.obj.PetriNet.Transition(
            "Openfile",
            "Openfile",
            None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: (
                        next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                            constants.DICT_KEY_LAYOUT_X] + 100
                    ),
                    constants.DICT_KEY_LAYOUT_Y: next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                     constants.DICT_KEY_LAYOUT_Y],
                    constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                    constants.DICT_KEY_LAYOUT_WIDTH: 25
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 0.0,
                    constants.DICT_KEY_PERF_STDEV: 0.0
                }
            }
        )
        openfile_trans_tag = self.create_trans_element_for_page(openfile_trans, document, non_silent_trans, group_name,
                                                                is_init_trans=True, is_openfile_trans=True)
        page_tag.appendChild(openfile_trans_tag)

        # create <arc> from 'Openfile' to 'next_CASE_ID'
        arc_optrans_to_place = pm4py.objects.petri_net.obj.PetriNet.Arc(
            openfile_trans, next_case_id_place, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                     constants.DICT_KEY_LAYOUT_X] + 50,
                    constants.DICT_KEY_LAYOUT_Y: next_case_id_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                        constants.DICT_KEY_LAYOUT_Y],
                }
            }
        )

        arc_optrans_to_place_tag = self.create_arc_element_for_page(arc_optrans_to_place, document, is_openEL_arc=True)
        page_tag.appendChild(arc_optrans_to_place_tag)
        # ------------------------------------------

        # -----------------------------------
        # setup OpenEL place
        # create <place>
        openEL_place = pm4py.objects.petri_net.obj.PetriNet.Place(
            "OpenEL", None, None, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: openfile_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                        constants.DICT_KEY_LAYOUT_X],
                    constants.DICT_KEY_LAYOUT_Y: (
                            openfile_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                constants.DICT_KEY_LAYOUT_Y] + 50
                    ),
                    constants.DICT_KEY_LAYOUT_HEIGHT: 15,
                    constants.DICT_KEY_LAYOUT_WIDTH: 40
                }
            }
        )
        openEL_place_tag = self.create_place_element_for_page(openEL_place, {}, {}, document,
                                                              is_openEL_place=True)
        page_tag.appendChild(openEL_place_tag)
        # create <arc> from 'OpenEL' to 'Openfile'
        arc_opplace_to_optrans = pm4py.objects.petri_net.obj.PetriNet.Arc(
            openEL_place, openfile_trans, weight=1, properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: openfile_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                     constants.DICT_KEY_LAYOUT_X] + 50,
                    constants.DICT_KEY_LAYOUT_Y: openfile_trans.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                        constants.DICT_KEY_LAYOUT_Y],
                }
            }
        )

        arc_opplace_to_optrans_tag = self.create_arc_element_for_page(arc_opplace_to_optrans, document, is_openEL_arc=True)
        page_tag.appendChild(arc_opplace_to_optrans_tag)
        # -----------------------------------

        # setup probability places
        arcs_with_prob = self.get_arcs_with_prob_info(petri_net)
        for key, arcs in arcs_with_prob.items():
            # the transitions between which the probability place has to be created
            transition_upper = None
            transition_lower = None
            probs_of_source_place = []
            for arc in arcs:
                if transition_upper is None:
                    transition_upper = arc.target
                if transition_lower is None:
                    transition_lower = arc.target

                trans_y = arc.target.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]
                transition_upper_y = transition_upper.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                    constants.DICT_KEY_LAYOUT_Y]
                transition_lower_y = transition_lower.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                    constants.DICT_KEY_LAYOUT_Y]

                if trans_y > transition_upper_y:
                    transition_upper = arc.target
                elif trans_y < transition_lower_y:
                    transition_lower = arc.target

                # store the probabilities
                probs_of_source_place.append(
                    (
                        arc.target.name,
                        arc.target.properties[constants.DICT_KEY_PROBA_INFO_PETRI]
                    )
                )

                # sort the probabilities list of souurce place
            probs_of_source_place.sort(key=lambda tup: tup[1], reverse=True)

            # create <place>
            prob_place = pm4py.objects.petri_net.obj.PetriNet.Place(
                "prob_" +
                str(transition_upper.properties[constants.DICT_KEY_TRANS_INDEX_PETRI]) +
                "_" +
                str(transition_lower.properties[constants.DICT_KEY_TRANS_INDEX_PETRI]),
                None, None, properties={
                    constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                        constants.DICT_KEY_LAYOUT_X: transition_lower.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                            constants.DICT_KEY_LAYOUT_X],
                        constants.DICT_KEY_LAYOUT_Y: (
                                                             transition_upper.properties[
                                                                 constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                 constants.DICT_KEY_LAYOUT_Y] +
                                                             transition_lower.properties[
                                                                 constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                 constants.DICT_KEY_LAYOUT_Y]
                                                     ) / 2,
                        constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                        constants.DICT_KEY_LAYOUT_WIDTH: 28
                    }
                }
            )
            place_tag = self.create_place_element_for_page(prob_place, {}, {}, document, is_decision_prob_place=True)
            page_tag.appendChild(place_tag)

            for arc in arcs:
                if arc.target == transition_lower:
                    arc_place_to_trans_layout_x = prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                      constants.DICT_KEY_LAYOUT_X] - 5
                    arc_trans_to_place_layout_x = prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                      constants.DICT_KEY_LAYOUT_X] + 20
                else:
                    arc_place_to_trans_layout_x = prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                      constants.DICT_KEY_LAYOUT_X] + 5
                    arc_trans_to_place_layout_x = prob_place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                      constants.DICT_KEY_LAYOUT_X] - 20

                # create arc_1
                arc_place_to_trans = pm4py.objects.petri_net.obj.PetriNet.Arc(
                    prob_place, arc.target, weight=1, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: arc_place_to_trans_layout_x,
                            constants.DICT_KEY_LAYOUT_Y: (
                                                                 prob_place.properties[
                                                                     constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                     constants.DICT_KEY_LAYOUT_Y] +
                                                                 arc.target.properties[
                                                                     constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                     constants.DICT_KEY_LAYOUT_Y]
                                                         ) / 2.06
                        }
                    }
                )
                arc_place_to_trans_tag = self.create_arc_element_for_page(arc_place_to_trans, document,
                                                                          is_decision_prob_arc=True)
                page_tag.appendChild(arc_place_to_trans_tag)
                # create arc_2
                arc_trans_to_place = pm4py.objects.petri_net.obj.PetriNet.Arc(
                    arc.target, prob_place, weight=1, properties={
                        constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                            constants.DICT_KEY_LAYOUT_X: arc_trans_to_place_layout_x,
                            constants.DICT_KEY_LAYOUT_Y: (
                                                                 prob_place.properties[
                                                                     constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                     constants.DICT_KEY_LAYOUT_Y] +
                                                                 arc.target.properties[
                                                                     constants.DICT_KEY_LAYOUT_INFO_PETRI][
                                                                     constants.DICT_KEY_LAYOUT_Y]
                                                         ) / 2.06
                        }
                    }
                )
                arc_trans_to_place_tag = self.create_arc_element_for_page(arc_trans_to_place, document,
                                                                          is_decision_prob_arc=True)
                page_tag.appendChild(arc_trans_to_place_tag)

                # update trans element with guard condition
                self.update_trans_element_with_guard_cond(
                    arc.target, trans_dict[str(arc.target.name)], document, probs_of_source_place
                )

        return page_tag

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
        globbox_tag = self.create_globbox_element_for_document(document, len(petri_net.transitions))
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

    def get_cpn_zip_file_path(self, event_log_id):
        cpn_file_path = self.get_cpn_file_path(event_log_id)
        sml_file_path = self.get_sml_file_path()
        cpn_zip_path = os.path.join(os.path.dirname(cpn_file_path),
                                    current_app.config["CPN_MODEL_DEFAULT_NAME"] + '.zip')
        with ZipFile(cpn_zip_path, 'w') as cpn_zip:
            cpn_zip.write(cpn_file_path, os.path.basename(cpn_file_path))
            cpn_zip.write(sml_file_path, os.path.basename(sml_file_path))

        # remove cpn model file
        os.remove(cpn_file_path)

        return cpn_zip_path

    def get_sml_file_path(self):
        sml_file_extension = 'sml'
        sml_file_path = os.path.join(
            current_app.config['DATA_FOLDER'],
            current_app.config["SML_FILE_DEFAULT_NAME"] +
            "." +
            sml_file_extension)
        return sml_file_path
