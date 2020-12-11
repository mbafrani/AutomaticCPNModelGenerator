import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from xml.dom.minidom import Document, Element
import pm4py
import flask
from werkzeug.exceptions import NotFound, UnsupportedMediaType, BadRequest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from services import CPNExportService
from util import constants


class TestCPNExportService(unittest.TestCase):

    def test_create_arc_element_for_page__trans_to_place(self):
        cpn_export_service = CPNExportService()
        arc_obj = MagicMock()
        arc_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20
            }
        }
        arc_obj.source = pm4py.objects.petri.petrinet.PetriNet.Transition(
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
        arc_obj.target = pm4py.objects.petri.petrinet.PetriNet.Place(
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
        document = Document()
        arc_element = cpn_export_service.create_arc_element_for_page(
            arc_obj, document
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
        execution_time_mean = str(
            arc_obj.source.properties[constants.DICT_KEY_PERF_INFO_PETRI][constants.DICT_KEY_PERF_MEAN]
        )
        execution_time_stdev = str(
            arc_obj.source.properties[constants.DICT_KEY_PERF_INFO_PETRI][constants.DICT_KEY_PERF_STDEV]
        )
        normal_distrib = str(
            "normal(" + execution_time_mean + "," + execution_time_stdev + ")"
        )
        self.assertEqual(
            str(constants.DECLARATION_COLOR_REQUEST_VARIABLE) + "@+" + str("Real.round(" + normal_distrib + ")"),
            text_element[0].firstChild.nodeValue
        )

    def test_create_arc_element_for_page__place_to_trans(self):
        cpn_export_service = CPNExportService()
        arc_obj = MagicMock()
        arc_obj.properties = {
            constants.DICT_KEY_LAYOUT_INFO_PETRI: {
                constants.DICT_KEY_LAYOUT_X: 10,
                constants.DICT_KEY_LAYOUT_Y: 20
            }
        }
        arc_obj.source = pm4py.objects.petri.petrinet.PetriNet.Place(
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
        arc_obj.target = pm4py.objects.petri.petrinet.PetriNet.Transition(
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
            constants.DECLARATION_COLOR_REQUEST_VARIABLE,
            text_element[0].firstChild.nodeValue
        )

    def test_create_page_element_for_document(self):
        cpn_export_service = CPNExportService()
        petri_net_obj = MagicMock()
        petri_net_obj.places = {'place1': {}, 'place2': {}}
        petri_net_obj.transitions = {'trans1': {}, 'trans2': {}}
        petri_net_obj.arcs = {'arc1': {}, 'arc2': {}, 'arc3': {}, 'arc4': {}}
        document = Document()
        cpn_export_service.create_place_element_for_page = MagicMock(
            side_effect=[document.createElement("place") for elem in petri_net_obj.places]
        )
        cpn_export_service.create_trans_element_for_page = MagicMock(
            side_effect=[document.createElement("trans") for elem in petri_net_obj.transitions]
        )
        cpn_export_service.create_arc_element_for_page = MagicMock(
            side_effect=[document.createElement("arc") for elem in petri_net_obj.arcs]
        )

        page_element = cpn_export_service.create_page_element_for_document(
            document, petri_net_obj, None, None, None
        )

        self.assertIsInstance(page_element, Element)
        self.assertEqual(1, len(page_element.getElementsByTagName("pageattr")))
        self.assertEqual(2, len(page_element.getElementsByTagName("place")))
        self.assertEqual(2, len(page_element.getElementsByTagName("trans")))
        self.assertEqual(4, len(page_element.getElementsByTagName("arc")))

    def test_create_cpn_model_from_petri_net(self):
        cpn_export_service = CPNExportService()
        document = Document()
        cpn_export_service.create_globbox_element_for_document = MagicMock(
            return_value=document.createElement("globbox")
        )
        cpn_export_service.create_page_element_for_document = MagicMock(
            return_value=document.createElement("page")
        )

        cpn_model = cpn_export_service.create_cpn_model_from_petri_net(None, None, None)

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

            expected_file_path = app.config['UPLOAD_FOLDER'] + "\\" + event_log_id + "\\" + app.config["CPN_MODEL_DEFAULT_NAME"] + ".cpn"
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


if __name__ == '__main__':
    unittest.main()
