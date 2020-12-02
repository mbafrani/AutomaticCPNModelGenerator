import pm4py
from flask import current_app
from xml.dom.minidom import DOMImplementation
import os
import json
import uuid

from util import constants


class CPNExportService:

    def __init__(self):
        pass

    # globbox element in the cpn file contains color set declarations
    def create_globbox_element_for_document(self, document):
        globbox_tag = document.createElement("globbox")

        # setup color set declarations

        color_tag = document.createElement("color")
        color_tag.setAttribute("id", str(uuid.uuid1().hex))

        colorid_tag = document.createElement("id")
        colorid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_REQUEST)))
        color_tag.appendChild(colorid_tag)

        colortimed_tag = document.createElement("timed")
        color_tag.appendChild(colortimed_tag)

        colorindex_tag = document.createElement("index")
        colorml_tag = document.createElement("ml")
        colorml_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_REQUEST_ITER_INDEX_START)))
        colorindex_tag.appendChild(colorml_tag)
        colorml_tag = document.createElement("ml")
        colorml_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_REQUEST_ITER_INDEX_END)))
        colorindex_tag.appendChild(colorml_tag)
        colorindexid_tag = document.createElement("id")
        colorindexid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_REQUEST_ITER_INSTANCE)))
        colorindex_tag.appendChild(colorindexid_tag)

        color_tag.appendChild(colorindex_tag)

        globbox_tag.appendChild(color_tag)

        # setup color set variables declarations

        var_tag = document.createElement("var")
        var_tag.setAttribute("id", str(uuid.uuid1().hex))

        vartype_tag = document.createElement("type")
        vartypeid_tag = document.createElement("id")
        vartypeid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_REQUEST)))
        vartype_tag.appendChild(vartypeid_tag)
        var_tag.appendChild(vartype_tag)

        varid_tag = document.createElement("id")
        varid_tag.appendChild(document.createTextNode(
            str(constants.DECLARATION_COLOR_REQUEST_VARIABLE)))
        var_tag.appendChild(varid_tag)

        globbox_tag.appendChild(var_tag)

        return globbox_tag

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
        for place in petri_net.places:
            place_tag = document.createElement("place")
            place_tag.setAttribute("id", str(place.name))

            posattr_tag = document.createElement("posattr")
            posattr_tag.setAttribute(
                "x", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            posattr_tag.setAttribute(
                "y", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
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
                "h", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][1][0]))
            ellipse_tag.setAttribute(
                "w", str(place.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]))
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
                place.properties[constants.LAYOUT_INFORMATION_PETRI][0][0] +
                place.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]
            ))
            # attribute position_y = place_y_position - place_height/2
            posattr_tag.setAttribute("y", str(
                place.properties[constants.LAYOUT_INFORMATION_PETRI][0][1] -
                (place.properties[constants.LAYOUT_INFORMATION_PETRI][1][0] / 2)
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
            text_tag.appendChild(document.createTextNode(
                str(constants.DECLARATION_COLOR_REQUEST)))
            type_tag.appendChild(text_tag)

            place_tag.appendChild(type_tag)

            # for places that are initial_marking, setup initial_marking tag at
            # top-right of the place
            if place in initial_marking.keys():
                initmark_tag = document.createElement("initmark")
                initmark_tag.setAttribute("id", str(uuid.uuid1().hex))

                posattr_tag = document.createElement("posattr")
                # initial_marking position_x = place_x_position + place_width
                posattr_tag.setAttribute("x", str(
                    place.properties[constants.LAYOUT_INFORMATION_PETRI][0][0] +
                    place.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]
                ))
                # initial_marking position_y = place_y_position +
                # place_height/2
                posattr_tag.setAttribute("y", str(
                    place.properties[constants.LAYOUT_INFORMATION_PETRI][0][1] +
                    (place.properties[constants.LAYOUT_INFORMATION_PETRI][1][0] / 2)
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
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_REQUEST_INSTANCES)))
                initmark_tag.appendChild(text_tag)

                place_tag.appendChild(initmark_tag)

            page_tag.appendChild(place_tag)

        # <trans>, setup for transition rectangles
        for trans in petri_net.transitions:
            trans_tag = document.createElement("trans")
            # remove hypens from the guid (or else cpntool will crash)
            trans_tag.setAttribute("id", str(trans.name).replace('-', ''))

            posattr_tag = document.createElement("posattr")
            posattr_tag.setAttribute(
                "x", str(trans.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            posattr_tag.setAttribute(
                "y", str(trans.properties[constants.LAYOUT_INFORMATION_PETRI][0][1]))
            trans_tag.appendChild(posattr_tag)

            fillattr_tag = document.createElement("fillattr")
            fillattr_tag.setAttribute("colour", "White")
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
                "h", str(trans.properties[constants.LAYOUT_INFORMATION_PETRI][1][0]))
            box_tag.setAttribute(
                "w", str(trans.properties[constants.LAYOUT_INFORMATION_PETRI][1][1]))
            trans_tag.appendChild(box_tag)

            time_tag = document.createElement("time")
            time_tag.setAttribute("id", str(uuid.uuid1().hex))

            posattr_tag = document.createElement("posattr")
            # time position_x = place_x_position + place_width/1.5
            posattr_tag.setAttribute("x", str(
                trans.properties[constants.LAYOUT_INFORMATION_PETRI][0][0] +
                (trans.properties[constants.LAYOUT_INFORMATION_PETRI][1][1] / 1.5)
            ))
            # time position_y = place_y_position - place_height/1.5
            posattr_tag.setAttribute("y", str(
                trans.properties[constants.LAYOUT_INFORMATION_PETRI][0][1] -
                (trans.properties[constants.LAYOUT_INFORMATION_PETRI][1][0] / 1.5)
            ))
            time_tag.appendChild(posattr_tag)

            fillattr_tag = document.createElement("fillattr")
            fillattr_tag.setAttribute("colour", "White")
            fillattr_tag.setAttribute("pattern", "Solid")
            fillattr_tag.setAttribute("filled", "false")
            time_tag.appendChild(fillattr_tag)

            lineattr_tag = document.createElement("lineattr")
            lineattr_tag.setAttribute("colour", "Teal")
            lineattr_tag.setAttribute("thick", "0")
            lineattr_tag.setAttribute("type", "Solid")
            time_tag.appendChild(lineattr_tag)

            textattr_tag = document.createElement("textattr")
            textattr_tag.setAttribute("colour", "Teal")
            textattr_tag.setAttribute("bold", "false")
            time_tag.appendChild(textattr_tag)

            text_tag = document.createElement("text")
            text_tag.appendChild(document.createTextNode("@+" + str(
                trans.properties[constants.PERFORMANCE_INFORMATION_PETRI]
            )))
            time_tag.appendChild(text_tag)

            trans_tag.appendChild(time_tag)

            page_tag.appendChild(trans_tag)

        # <arcs>, setup for arcs
        for arc in petri_net.arcs:
            # identify the place and transition ends of the arc
            is_target_trans = isinstance(
                arc.target, pm4py.objects.petri.petrinet.PetriNet.Transition)
            is_target_place = isinstance(
                arc.target, pm4py.objects.petri.petrinet.PetriNet.Place)

            # identify orientation of the arc, Place->Trans or Trans->Place
            orientation = constants.PLACE_TO_TRANS_ORIENTATION if is_target_trans else constants.TRANS_TO_PLACE_ORIENTATION

            # remove hypens from the transend_idref (since we removed the same from transition id above)
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
                "x", str(arc.properties[constants.LAYOUT_INFORMATION_PETRI][0][0]))
            # move y position by 5 else the arc annotation will end up lying on
            # the arc
            posattr_tag.setAttribute(
                "y", str(arc.properties[constants.LAYOUT_INFORMATION_PETRI][0][1] + 5))
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
            textattr_tag.setAttribute("colour", "Black")
            textattr_tag.setAttribute("bold", "false")
            annot_tag.appendChild(textattr_tag)

            text_tag = document.createElement("text")
            # TODO: "@+0" is a dummy. Needs to be removed later
            # For now there's no execution time information on the arc transition->place,
            # Once it's implemented replace the dummy "@+0" by the execution
            # time stored in arc.properties[PERFORMANCE_INFORMATION_PETRI]
            if(is_target_place):
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_REQUEST_VARIABLE) + "@+0"))
            else:
                text_tag.appendChild(document.createTextNode(
                    str(constants.DECLARATION_COLOR_REQUEST_VARIABLE)))
            annot_tag.appendChild(text_tag)

            arc_tag.appendChild(annot_tag)

            page_tag.appendChild(arc_tag)

        return page_tag

    # Genarates a cpn dom object filled with information from the petri net

    def create_cpn_model_from_petri_net(
            self,
            petri_net,
            initial_marking,
            final_marking,
            parameters=None):

        custom_dom_imp = DOMImplementation()

        # <!DOCTYPE workspaceElements PUBLIC "-//CPN//DTD CPNXML 1.0//EN" "http://www.daimi.au.dk/~cpntools/bin/DTD/2/cpn.dtd">
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
            document, petri_net, initial_marking, final_marking, parameters=None)
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
        cpn_file_path = self.get_cpn_file_path(event_log_id)
        # <?xml version="1.0" encoding="iso-8859-1"?>
        xml_str = model.toprettyxml(encoding="iso-8859-1")
        with open(cpn_file_path, "wb") as file:
            file.write(xml_str)
