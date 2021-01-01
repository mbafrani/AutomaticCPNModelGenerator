from flask import Blueprint, send_from_directory
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError

wapp_page = Blueprint("wapp", __name__)


@wapp_page.route("/", methods=["GET"])
def send_index_page():
    return send_from_directory("wapp", "index.html")


@wapp_page.route("/views/<path:path>", methods=["GET"])
def send_views(path):
    return send_from_directory("wapp/views", path)


@wapp_page.route("/js/<path:path>", methods=["GET"])
def send_js(path):
    return send_from_directory("wapp/js", path, mimetype="text/javascript")


@wapp_page.route("/css/<path:path>", methods=["GET"])
def send_css(path):
    return send_from_directory("wapp/css", path)


@wapp_page.route("/images/<path:path>", methods=["GET"])
def send_images(path):
    return send_from_directory("wapp/images", path)
