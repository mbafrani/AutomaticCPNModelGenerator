from flask import Flask
from flask.blueprints import Blueprint
import os

import config
import routes

app = Flask(__name__)

app.debug = config.DEBUG
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, config.UPLOAD_FOLDER)
app.config["TEMP_FOLDER"] = os.path.join(app.root_path, config.TEMP_FOLDER)
app.config["EVENT_LOG_DEFAULT_NAME"] = config.EVENT_LOG_DEFAULT_NAME
app.config["PROCESS_MODEL_DEFAULT_NAME"] = config.PROCESS_MODEL_DEFAULT_NAME
app.config["CPN_MODEL_DEFAULT_NAME"] = config.CPN_MODEL_DEFAULT_NAME

for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        app.register_blueprint(blueprint, url_prefix=config.APPLICATION_ROOT)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)