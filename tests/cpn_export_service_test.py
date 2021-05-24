import unittest
import uuid
from unittest.mock import MagicMock, patch
import sys
import os
from xml.dom.minidom import Document, Element
import pm4py
import flask
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from api.services import CPNExportService
from api.util import constants


class TestCPNExportService(unittest.TestCase):

    @unittest.skip
    def test_create_globbox_element_for_document(self):
        cpn_export_service = CPNExportService()
        document = Document()
        num_of_trans = 3
        globbox_element = cpn_export_service.create_globbox_element_for_document(document, num_of_trans)

        self.assertIsInstance(globbox_element, Element)
        self.assertEqual(3, len(globbox_element.getElementsByTagName("color")))
        self.assertEqual(2, len(globbox_element.getElementsByTagName("timed")))
        self.assertEqual(2, len(globbox_element.getElementsByTagName("var")))
        self.assertEqual(1, len(globbox_element.getElementsByTagName("enum")))
        id_element = globbox_element.getElementsByTagName("id")
        self.assertEqual(str(constants.DECLARATION_COLOR_CASE_ID), id_element[0].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_PROBABILITY), id_element[1].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_RES_CAPACITY), id_element[2].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE), id_element[3].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_CASE_ID), id_element[4].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE), id_element[5].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_PROBABILITY), id_element[6].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_COLOR_PROBABILITY_VARIABLE), id_element[7].firstChild.nodeValue)
        self.assertEqual(str(constants.DECLARATION_BLOCK_EXEC_TIME_ID), id_element[8].firstChild.nodeValue)

        ml_elements = globbox_element.getElementsByTagName("ml")
        self.assertEqual(num_of_trans + 2, len(ml_elements))

        for i in range(num_of_trans+2):
            if i == 0:
                self.assertEqual(str(constants.DECLARATION_COLOR_NORMAL_DISTRIB_FUNCTION), ml_elements[i].firstChild.nodeValue)
            elif i == 1:
                self.assertEqual(str(constants.DECLARATION_COLOR_EXP_DISTRIB_FUNCTION), ml_elements[i].firstChild.nodeValue)
            else:
                self.assertEqual(str(constants.DECLARATION_ASSIGNMENT_EXEC_TIME).format(i-2), ml_elements[i].firstChild.nodeValue)

    def test_create_place_element_for_page(self):
        cpn_export_service = CPNExportService()
        place_obj = MagicMock()
        place_obj.name = "place1"
        place_obj.__str__ = MagicMock(return_value="place1")
        place_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
                constants.DICT_KEY_LAYOUT_HEIGHT: 30,
                constants.DICT_KEY_LAYOUT_WIDTH: 30
            }
        }
        document = Document()
        place_element = cpn_export_service.create_place_element_for_page(
            place_obj, {}, {}, document
        )

        self.assertIsInstance(place_element, Element)
        self.assertEqual(place_obj.name, place_element.getAttribute("id"))
        posattr_element = place_element.getElementsByTagName("posattr")
        self.assertEqual(2, len(posattr_element))
        self.assertEqual(
            str(place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X]),
            posattr_element[0].getAttribute("x")
        )
        self.assertEqual(
            str(place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]),
            posattr_element[0].getAttribute("y")
        )
        self.assertEqual(2, len(place_element.getElementsByTagName("fillattr")))
        self.assertEqual(2, len(place_element.getElementsByTagName("lineattr")))
        self.assertEqual(2, len(place_element.getElementsByTagName("textattr")))
        text_element = place_element.getElementsByTagName("text")
        self.assertEqual(str(place_obj), text_element[0].firstChild.nodeValue)
        ellipse_element = place_element.getElementsByTagName("ellipse")
        self.assertEqual(1, len(ellipse_element))
        self.assertEqual(
            str(place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_HEIGHT]),
            ellipse_element[0].getAttribute("h")
        )
        self.assertEqual(
            str(place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH]),
            ellipse_element[0].getAttribute("w")
        )
        self.assertEqual(1, len(place_element.getElementsByTagName("token")))
        self.assertEqual(1, len(place_element.getElementsByTagName("marking")))
        self.assertEqual(
            str(place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] + (
                place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH]
            )),
            posattr_element[1].getAttribute("x")
        )
        self.assertEqual(
            str(
                place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] - (
                    place_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_HEIGHT] / 2
                )),
            posattr_element[1].getAttribute("y")
        )
        self.assertEqual(2, len(text_element))
        self.assertEqual(str(constants.DECLARATION_COLOR_CASE_ID), text_element[1].firstChild.nodeValue)

    def test_create_place_element_for_page__with_initial_markings(self):
        cpn_export_service = CPNExportService()

        place_case = MagicMock()
        place_case.name = "next_CASE_ID"
        place_case.__str__ = MagicMock(return_value="next_CASE_ID")
        place_case.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
                constants.DICT_KEY_LAYOUT_HEIGHT: 30,
                constants.DICT_KEY_LAYOUT_WIDTH: 30
            }
        }
        place_prob = MagicMock()
        place_prob.name = "prob_1"
        place_prob.__str__ = MagicMock(return_value="prob_1")
        place_prob.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
                constants.DICT_KEY_LAYOUT_HEIGHT: 30,
                constants.DICT_KEY_LAYOUT_WIDTH: 30
            }
        }
        place_cap = MagicMock()
        place_cap.name = "cap_1"
        place_cap.__str__ = MagicMock(return_value="cap_1")
        place_cap.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 30,
                constants.DICT_KEY_LAYOUT_Y: 40,
                constants.DICT_KEY_LAYOUT_HEIGHT: 30,
                constants.DICT_KEY_LAYOUT_WIDTH: 30
            }
        }
        res_cap = 2

        places = [place_case, place_prob, place_cap]

        for i, place in enumerate(places):
            document = Document()
            if i == 0:
                place_element = cpn_export_service.create_place_element_for_page(
                    place, {place: place}, {}, document, is_next_case_id_place=True
                )
            elif i == 1:
                place_element = cpn_export_service.create_place_element_for_page(
                    place, {place: place}, {}, document, is_decision_prob_place=True
                )
            else:
                place_element = cpn_export_service.create_place_element_for_page(
                    place, {place: place}, {}, document, is_res_cap_place=True, res_capacity=res_cap
                )

            self.assertIsInstance(place_element, Element)
            self.assertEqual(place.name, place_element.getAttribute("id"))
            posattr_element = place_element.getElementsByTagName("posattr")
            self.assertEqual(3, len(posattr_element))
            self.assertEqual(3, len(place_element.getElementsByTagName("fillattr")))
            self.assertEqual(3, len(place_element.getElementsByTagName("lineattr")))
            self.assertEqual(3, len(place_element.getElementsByTagName("textattr")))

            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X]),
                posattr_element[0].getAttribute("x")
            )
            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]),
                posattr_element[0].getAttribute("y")
            )

            text_element = place_element.getElementsByTagName("text")
            ellipse_element = place_element.getElementsByTagName("ellipse")
            self.assertEqual(1, len(ellipse_element))
            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_HEIGHT]),
                ellipse_element[0].getAttribute("h")
            )
            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH]),
                ellipse_element[0].getAttribute("w")
            )
            self.assertEqual(1, len(place_element.getElementsByTagName("token")))
            self.assertEqual(1, len(place_element.getElementsByTagName("marking")))
            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] + (
                    place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH]
                )),
                posattr_element[1].getAttribute("x")
            )
            self.assertEqual(
                str(
                    place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] - (
                        place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                        [constants.DICT_KEY_LAYOUT_HEIGHT] / 2
                    )),
                posattr_element[1].getAttribute("y")
            )
            self.assertEqual(3, len(text_element))
            self.assertEqual(str(place), text_element[0].firstChild.nodeValue)
            if i == 0:
                self.assertEqual(str(constants.DECLARATION_COLOR_CASE_ID), text_element[1].firstChild.nodeValue)
            elif i == 1:
                self.assertEqual(str(constants.DECLARATION_COLOR_PROBABILITY), text_element[1].firstChild.nodeValue)
            else:
                self.assertEqual(str(constants.DECLARATION_COLOR_RES_CAPACITY), text_element[1].firstChild.nodeValue)

            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_X] + (
                        place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                        [constants.DICT_KEY_LAYOUT_WIDTH]
                )),
                posattr_element[2].getAttribute("x")
            )
            self.assertEqual(
                str(place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                    [constants.DICT_KEY_LAYOUT_Y] + (
                        place.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI]
                        [constants.DICT_KEY_LAYOUT_HEIGHT] / 2
                )),
                posattr_element[2].getAttribute("y")
            )
            if i == 0:
                self.assertEqual(str(1), text_element[2].firstChild.nodeValue)
            elif i == 1:
                self.assertEqual(str(constants.DECLARATION_COLOR_PROBABILITY_FUNCTION), text_element[2].firstChild.nodeValue)
            else:
                self.assertEqual(str(res_cap) + '`' + str(constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE),
                                 text_element[2].firstChild.nodeValue)



    def test_create_trans_element_for_page(self):
        cpn_export_service = CPNExportService()
        trans_obj = MagicMock()
        trans_obj.name = "trans-1-abc"
        trans_obj.label = "trans1"
        trans_obj.__str__ = MagicMock(return_value="trans1")
        trans_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
                constants.DICT_KEY_LAYOUT_HEIGHT: 30,
                constants.DICT_KEY_LAYOUT_WIDTH: 50
            },
            constants.DICT_KEY_PERF_INFO_PETRI: {
                constants.DICT_KEY_PERF_MEAN: 30,
                constants.DICT_KEY_PERF_STDEV: 5
            },
            constants.DICT_KEY_TRANS_INDEX_PETRI: 1
        }
        document = Document()
        trans_element = cpn_export_service.create_trans_element_for_page(
            trans_obj, document
        )

        self.assertIsInstance(trans_element, Element)
        self.assertEqual(str(trans_obj.name).replace('-', ''), trans_element.getAttribute("id"))
        posattr_element = trans_element.getElementsByTagName("posattr")
        self.assertEqual(2, len(posattr_element))
        self.assertEqual(
            str(trans_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X]),
            posattr_element[0].getAttribute("x")
        )
        self.assertEqual(
            str(trans_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y]),
            posattr_element[0].getAttribute("y")
        )
        self.assertEqual(
            str(trans_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] +
                (
                    trans_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_WIDTH] + 15
                )),
            posattr_element[1].getAttribute("x")
        )
        self.assertEqual(
            str(trans_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] -
                (
                    trans_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_HEIGHT] / 1.2
                ) - 2),
            posattr_element[1].getAttribute("y")
        )
        fillattr_element = trans_element.getElementsByTagName("fillattr")
        self.assertEqual("Silver", fillattr_element[0].getAttribute("colour"))
        self.assertEqual("White", fillattr_element[1].getAttribute("colour"))
        self.assertEqual(2, len(trans_element.getElementsByTagName("lineattr")))
        self.assertEqual(2, len(trans_element.getElementsByTagName("textattr")))
        text_element = trans_element.getElementsByTagName("text")
        self.assertEqual(str(trans_obj), text_element[0].firstChild.nodeValue)

        self.assertEqual(1, len(trans_element.getElementsByTagName("code")))
        normal_distrib = "N(" + str(trans_obj.properties[constants.DICT_KEY_PERF_INFO_PETRI][constants.DICT_KEY_PERF_MEAN]) \
                         + ", " + str(trans_obj.properties[constants.DICT_KEY_PERF_INFO_PETRI][constants.DICT_KEY_PERF_STDEV]) + ")"

        dist_fun = constants.DECLARATION_CODE_SEGMENT_INPUT + "\n" + \
                   str(constants.DECLARATION_CODE_SEGMENT_ACTION).format(
                       constants.DECLARATION_VAR_EXEC_TIME.format(trans_obj.properties[constants.DICT_KEY_TRANS_INDEX_PETRI]),
                       str(trans_obj),
                       normal_distrib
                   )

        self.assertEqual(str(dist_fun), text_element[1].firstChild.nodeValue)

    def test_create_arc_element_for_page__trans_to_place(self):
        cpn_export_service = CPNExportService()
        arc_obj = MagicMock()
        arc_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20
            }
        }
        trans1_index = 1
        arc_obj.source = pm4py.objects.petri_net.obj.PetriNet.Transition(
            'trans-1-abc', None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 10,
                    constants.DICT_KEY_LAYOUT_Y: 20
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 30,
                    constants.DICT_KEY_PERF_STDEV: 5
                },
                constants.DICT_KEY_TRANS_INDEX_PETRI: trans1_index
            }
        )
        arc_obj.target = pm4py.objects.petri_net.obj.PetriNet.Place(
            'place1', None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 10,
                    constants.DICT_KEY_LAYOUT_Y: 20
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 30,
                    constants.DICT_KEY_PERF_STDEV: 5
                }
            }
        )
        for i in range(4):
            document = Document()
            if i==0:
                arc_element = cpn_export_service.create_arc_element_for_page(
                    arc_obj, document
                )
            elif i==1:
                arrival_rate = 150
                arc_element = cpn_export_service.create_arc_element_for_page(
                    arc_obj, document, is_next_case_id_arc=True, arrival_rate=arrival_rate
                )
            elif i == 2:
                arc_element = cpn_export_service.create_arc_element_for_page(
                    arc_obj, document, is_decision_prob_arc=True
                )
            else:
                arc_element = cpn_export_service.create_arc_element_for_page(
                    arc_obj, document, is_res_cap_arc=True
                )

            self.assertIsInstance(arc_element, Element)
            self.assertEqual(constants.TRANS_TO_PLACE_ORIENTATION, arc_element.getAttribute("orientation"))
            self.assertEqual(1, len(arc_element.getElementsByTagName("arrowattr")))
            transend_element = arc_element.getElementsByTagName("transend")
            self.assertEqual(1, len(transend_element))
            self.assertEqual(
                arc_obj.source.name.replace('-', ''),
                transend_element[0].getAttribute("idref")
            )
            placeend_element = arc_element.getElementsByTagName("placeend")
            self.assertEqual(1, len(placeend_element))
            self.assertEqual(
                arc_obj.target.name,
                placeend_element[0].getAttribute("idref")
            )
            posattr_element = arc_element.getElementsByTagName("posattr")
            self.assertEqual(2, len(posattr_element))
            if i==1:
                pos_x = str(arc_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X] + 18)
            else:
                pos_x = str(arc_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X])
            pos_y = str(arc_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] + 5)
            self.assertEqual(pos_x, posattr_element[1].getAttribute("x"))
            self.assertEqual(pos_y, posattr_element[1].getAttribute("y"))
            self.assertEqual(2, len(arc_element.getElementsByTagName("fillattr")))
            self.assertEqual(2, len(arc_element.getElementsByTagName("lineattr")))
            self.assertEqual(2, len(arc_element.getElementsByTagName("textattr")))
            text_element = arc_element.getElementsByTagName("text")
            self.assertEqual(1, len(text_element))

            if i==0:
                self.assertEqual(
                    (str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE) + "@+(!" +
                    str(constants.DECLARATION_VAR_EXEC_TIME).format(trans1_index) + ")"),
                    text_element[0].firstChild.nodeValue
                )
            elif i==1:
                self.assertEqual(
                    str(constants.DECLARATION_COLOR_CASE_ID_VARIABLE + "+1@+Exp(" + str(arrival_rate) + ")"),
                    text_element[0].firstChild.nodeValue
                )
            elif i==2:
                self.assertEqual(
                    str(constants.DECLARATION_COLOR_PROBABILITY_FUNCTION), text_element[0].firstChild.nodeValue
                )
            else:
                self.assertEqual(
                    (str(constants.DECLARATION_COLOR_RES_CAPACITY_VARIABLE) + "@+(!" +
                     str(constants.DECLARATION_VAR_EXEC_TIME).format(trans1_index) + ")"),
                    text_element[0].firstChild.nodeValue
                )

    def test_create_arc_element_for_page__place_to_trans(self):
        cpn_export_service = CPNExportService()
        res_cap = 2
        arc_obj = MagicMock()
        arc_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20
            }
        }
        arc_obj.source = pm4py.objects.petri_net.obj.PetriNet.Place(
            'place1', None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 10,
                    constants.DICT_KEY_LAYOUT_Y: 20
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 30,
                    constants.DICT_KEY_PERF_STDEV: 5
                },
                constants.DICT_KEY_PERF_RES_CAP: res_cap
            }
        )
        arc_obj.target = pm4py.objects.petri_net.obj.PetriNet.Transition(
            'trans-1-abc', None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 10,
                    constants.DICT_KEY_LAYOUT_Y: 20
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 30,
                    constants.DICT_KEY_PERF_STDEV: 5
                }
            }
        )
        document = Document()
        arc_element = cpn_export_service.create_arc_element_for_page(
            arc_obj, document
        )

        self.assertIsInstance(arc_element, Element)
        self.assertEqual(constants.PLACE_TO_TRANS_ORIENTATION, arc_element.getAttribute("orientation"))
        self.assertEqual(1, len(arc_element.getElementsByTagName("arrowattr")))
        transend_element = arc_element.getElementsByTagName("transend")
        self.assertEqual(1, len(transend_element))
        self.assertEqual(
            arc_obj.target.name.replace('-', ''),
            transend_element[0].getAttribute("idref")
        )
        placeend_element = arc_element.getElementsByTagName("placeend")
        self.assertEqual(1, len(placeend_element))
        self.assertEqual(
            arc_obj.source.name,
            placeend_element[0].getAttribute("idref")
        )
        posattr_element = arc_element.getElementsByTagName("posattr")
        self.assertEqual(2, len(posattr_element))
        self.assertEqual(
            str(arc_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_X]),
            posattr_element[1].getAttribute("x")
        )
        self.assertEqual(
            str(arc_obj.properties[constants.DICT_KEY_LAYOUT_INFO_PETRI][constants.DICT_KEY_LAYOUT_Y] + 5),
            posattr_element[1].getAttribute("y")
        )
        self.assertEqual(2, len(arc_element.getElementsByTagName("fillattr")))
        self.assertEqual(2, len(arc_element.getElementsByTagName("lineattr")))
        self.assertEqual(2, len(arc_element.getElementsByTagName("textattr")))
        text_element = arc_element.getElementsByTagName("text")
        self.assertEqual(1, len(text_element))
        self.assertEqual(
            constants.DECLARATION_COLOR_CASE_ID_VARIABLE,
            text_element[0].firstChild.nodeValue
        )

    def test_create_page_element_for_document(self):
        cpn_export_service = CPNExportService()
        petri_net_obj = MagicMock()

        place_obj1 = MagicMock()
        place_obj1.name = "source"
        place_obj1.__str__ = MagicMock(return_value="source")
        place_obj1.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
            }
        }
        place_obj2 = MagicMock()
        place_obj2.name = "place2"
        place_obj2.__str__ = MagicMock(return_value="place2")
        place_obj2.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
            }
        }

        petri_net_obj.places = [place_obj1, place_obj2]

        res_cap1, res_cap2 = 1, 2
        trans_1 = pm4py.objects.petri_net.obj.PetriNet.Transition(
            'trans_1',
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 10,
                    constants.DICT_KEY_LAYOUT_Y: 20,
                    constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                    constants.DICT_KEY_LAYOUT_WIDTH: 25
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_RES_CAP: res_cap1
                }
            })
        trans_2 = pm4py.objects.petri_net.obj.PetriNet.Transition(
            'trans_2',
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 20,
                    constants.DICT_KEY_LAYOUT_Y: 30,
                    constants.DICT_KEY_LAYOUT_HEIGHT: 10,
                    constants.DICT_KEY_LAYOUT_WIDTH: 25
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_RES_CAP: res_cap2
                }
            })

        petri_net_obj.transitions = {trans_1, trans_2}
        petri_net_obj.arcs = {'arc1': {}, 'arc2': {}, 'arc3': {}, 'arc4': {}}
        document = Document()
        places_tag = []
        for p in petri_net_obj.places:
            places_tag.append(document.createElement("place"))

        cpn_export_service.create_place_element_for_page = MagicMock(
            side_effect =[document.createElement("place") for i in range(len(petri_net_obj.places)+len(petri_net_obj.transitions)+1)]
        )
        cpn_export_service.create_trans_element_for_page = MagicMock(
            side_effect =[document.createElement("trans") for i in range(len(petri_net_obj.transitions)+1)]
        )
        cpn_export_service.create_arc_element_for_page = MagicMock(
            side_effect =[document.createElement("arc") for i in range(len(petri_net_obj.arcs)+(len(petri_net_obj.transitions)*2)+3)]
        )
        cpn_export_service.get_arcs_with_prob_info = MagicMock(
            return_value={}
        )
        page_element = cpn_export_service.create_page_element_for_document(
            document, petri_net_obj, None, None, None
        )

        self.assertIsInstance(page_element, Element)
        self.assertEqual(1, len(page_element.getElementsByTagName("pageattr")))
        # self.assertEqual(len(petri_net_obj.places)+len(petri_net_obj.transitions)+1, len(page_element.getElementsByTagName("place")))
        self.assertEqual(len(petri_net_obj.transitions)+1, len(page_element.getElementsByTagName("trans")))
        # self.assertEqual(len(petri_net_obj.arcs)+(len(petri_net_obj.transitions)*2)+3, len(page_element.getElementsByTagName("arc")))

    def test_create_cpn_model_from_petri_net(self):
        cpn_export_service = CPNExportService()
        obj = MagicMock()
        arc1 = MagicMock()
        obj.arcs = {arc1.source: pm4py.objects.petri_net.obj.PetriNet.Place(
            'place1', None, None,
            properties={
                constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                    constants.DICT_KEY_LAYOUT_X: 10,
                    constants.DICT_KEY_LAYOUT_Y: 20
                },
                constants.DICT_KEY_PERF_INFO_PETRI: {
                    constants.DICT_KEY_PERF_MEAN: 30,
                    constants.DICT_KEY_PERF_STDEV: 5
                }
            }
        )}
        document = Document()
        cpn_export_service.create_globbox_element_for_document = MagicMock(
            return_value=document.createElement("globbox")
        )
        cpn_export_service.create_page_element_for_document = MagicMock(
            return_value=document.createElement("page")
        )
        cpn_export_service.get_arcs_with_prob_info = MagicMock(
            return_value={'p_1': MagicMock()}
        )
        cpn_model = cpn_export_service.create_cpn_model_from_petri_net(obj, None, None)

        self.assertIsInstance(cpn_model, Document)
        self.assertEqual("workspaceElements", cpn_model.doctype.name)
        self.assertEqual("-//CPN//DTD CPNXML 1.0//EN", cpn_model.doctype.publicId)
        self.assertEqual("http://www.daimi.au.dk/~cpntools/bin/DTD/2/cpn.dtd", cpn_model.doctype.systemId)
        self.assertEqual(1, len(cpn_model.getElementsByTagName("workspaceElements")))
        self.assertEqual(1, len(cpn_model.getElementsByTagName("generator")))
        self.assertEqual(1, len(cpn_model.getElementsByTagName("cpnet")))
        self.assertEqual(1, len(cpn_model.getElementsByTagName("globbox")))
        self.assertEqual(1, len(cpn_model.getElementsByTagName("page")))

    def test_get_cpn_file_path(self):
        app = flask.Flask(__name__)
        with app.app_context():
            cpn_export_service = CPNExportService()
            event_log_id = "12345-6789-abc"
            app.config["UPLOAD_FOLDER"] = "dummy_folder"
            app.config["CPN_MODEL_DEFAULT_NAME"] = "default"

            cpn_file_path = cpn_export_service.get_cpn_file_path(event_log_id)

            # check if os is windows ('nt)
            if os.name == 'nt':
                expected_file_path = app.config['UPLOAD_FOLDER'] + "\\" + event_log_id + "\\" + app.config["CPN_MODEL_DEFAULT_NAME"] + ".cpn"
            else:
                expected_file_path = app.config['UPLOAD_FOLDER'] + "/" + event_log_id + "/" + app.config["CPN_MODEL_DEFAULT_NAME"] + ".cpn"
            self.assertEqual(expected_file_path, cpn_file_path)

    def test_save_cpn_model(self):
        cpn_export_service = CPNExportService()
        model_obj = MagicMock()
        model_obj.toprettyxml = MagicMock(return_value="<xml huge string>".encode())
        event_log_id = "12345-6789-abc"
        output_data_path = os.path.join(os.path.dirname(__file__), "data", "output", event_log_id + ".cpn")
        cpn_export_service.get_cpn_file_path = MagicMock(return_value=output_data_path)

        cpn_export_service.save_cpn_model(model_obj, event_log_id)

        cpn_export_service.get_cpn_file_path.assert_called_with(event_log_id)
        model_obj.toprettyxml.assert_called_with(encoding="iso-8859-1")

    def test_get_arcs_with_prob_info(self):
        cpn_export_service = CPNExportService()
        petri_net_obj = MagicMock()
        petri_net_obj.arcs = []
        for i in range(4):
            arc = MagicMock()
            arc.source = pm4py.objects.petri_net.obj.PetriNet.Place('p_' + str(i))
            petri_net_obj.arcs.append(arc)
        arc1 = MagicMock()
        arc1.source = pm4py.objects.petri_net.obj.PetriNet.Place('p_1')
        petri_net_obj.arcs.append(arc1)
        arc3 = MagicMock()
        arc3.source = pm4py.objects.petri_net.obj.PetriNet.Place('p_3')
        petri_net_obj.arcs.append(arc3)

        arcs = cpn_export_service.get_arcs_with_prob_info(petri_net_obj)
        self.assertEqual(2, len(arcs))
        self.assertIn('p_1', arcs.keys())
        self.assertIn('p_3', arcs.keys())

    def test_update_trans_element_with_guard_cond(self):
        cpn_export_service = CPNExportService()
        trans_tag = Element('trans')
        trans_obj = MagicMock()
        trans_obj.name = "trans-1-abc"
        trans_obj.label = "trans1"
        trans_obj.__str__ = MagicMock(return_value="trans1")
        trans_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20,
                constants.DICT_KEY_LAYOUT_HEIGHT: 30,
                constants.DICT_KEY_LAYOUT_WIDTH: 50
            },
            constants.DICT_KEY_PROBA_INFO_PETRI: 75
        }
        document = Document()

        cpn_export_service.update_trans_element_with_guard_cond(
            trans_obj,
            trans_tag,
            document,
            [(trans_obj.name, trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI]), ("trans-2-abc", 25)]
        )
        cond_tag = trans_tag.getElementsByTagName('cond')
        self.assertEqual(1, len(cond_tag))
        cond_text = cond_tag[0].getElementsByTagName('text')
        self.assertEqual('[p < 75]', cond_text[0].firstChild.nodeValue)

        trans_tag = Element('trans')
        trans_obj.name = "trans-2-abc"
        trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI] = 25
        cpn_export_service.update_trans_element_with_guard_cond(
            trans_obj,
            trans_tag,
            document,
            [("trans-1-abc", 75), (trans_obj.name, trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI])]
        )
        cond_tag = trans_tag.getElementsByTagName('cond')
        self.assertEqual(1, len(cond_tag))
        cond_text = cond_tag[0].getElementsByTagName('text')
        self.assertEqual('[p >= 75]', cond_text[0].firstChild.nodeValue)

        trans_tag = Element('trans')
        trans_obj.name = "trans-1-abc"
        trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI] = 50
        cpn_export_service.update_trans_element_with_guard_cond(
            trans_obj,
            trans_tag,
            document,
            [(trans_obj.name, trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI]), ("trans-2-abc", 50)]
        )
        cond_tag = trans_tag.getElementsByTagName('cond')
        self.assertEqual(1, len(cond_tag))
        cond_text = cond_tag[0].getElementsByTagName('text')
        self.assertEqual('[p < 50]', cond_text[0].firstChild.nodeValue)

        trans_tag = Element('trans')
        trans_obj.name = "trans-2-abc"
        trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI] = 50
        cpn_export_service.update_trans_element_with_guard_cond(
            trans_obj,
            trans_tag,
            document,
            [("trans-1-abc", 50), (trans_obj.name, trans_obj.properties[constants.DICT_KEY_PROBA_INFO_PETRI])]
        )
        cond_tag = trans_tag.getElementsByTagName('cond')
        self.assertEqual(1, len(cond_tag))
        cond_text = cond_tag[0].getElementsByTagName('text')
        self.assertEqual('[p >= 50]', cond_text[0].firstChild.nodeValue)


if __name__ == '__main__':
    unittest.main()
