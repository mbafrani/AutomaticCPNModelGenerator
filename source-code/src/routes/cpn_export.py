from flask import Blueprint

cpn_export_page = Blueprint("cpn_export", __name__)

@cpn_export_page.route('/cpn-export')
def hello_world():
    return 'Hello, World!'
