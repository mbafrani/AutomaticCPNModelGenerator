from flask import Flask
from flask.blueprints import Blueprint
import os

import config
import api.routes as api_routes
import wapp.route as wapp_page

app = Flask(__name__, static_url_path="/wapp/")

app.debug = config.DEBUG
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, config.UPLOAD_FOLDER)
app.config["TEMP_FOLDER"] = os.path.join(app.root_path, config.TEMP_FOLDER)
app.config["EVENT_LOG_DEFAULT_NAME"] = config.EVENT_LOG_DEFAULT_NAME
app.config["PROCESS_MODEL_DEFAULT_NAME"] = config.PROCESS_MODEL_DEFAULT_NAME
app.config["CPN_MODEL_DEFAULT_NAME"] = config.CPN_MODEL_DEFAULT_NAME

# register api routes
for blueprint in vars(api_routes).values():
    if isinstance(blueprint, Blueprint):
        app.register_blueprint(blueprint, url_prefix=config.API_APPLICATION_ROOT)

# register wapp route
for blueprint in vars(wapp_page).values():
    if isinstance(blueprint, Blueprint):
        app.register_blueprint(blueprint, url_prefix=config.WAPP_APPLICATION_ROOT)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
    print("App running on: " + config.HOST + ":" + str(config.PORT))
