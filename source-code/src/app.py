from flask import Flask
from flask.blueprints import Blueprint

import config
import routes

app = Flask(__name__)

app.debug = config.DEBUG

for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        app.register_blueprint(blueprint, url_prefix=config.APPLICATION_ROOT)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)