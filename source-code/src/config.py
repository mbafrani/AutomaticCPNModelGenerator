import logging
import os

DEBUG = os.getenv("ENVIRONMENT") == "DEV"
APPLICATION_ROOT = os.getenv("APPLICATION_APPLICATION_ROOT", "/")
HOST = os.getenv("APPLICATION_HOST")
PORT = int(os.getenv("APPLICATION_PORT", "5000"))

UPLOAD_FOLDER = os.path.join('data', 'uploads')
TEMP_FOLDER = os.path.join('data', 'tmp')
EVENT_LOG_DEFAULT_NAME = "event-log"
PROCESS_MODEL_DEFAULT_NAME = "process-model-inductive"
CPN_MODEL_DEFAULT_NAME = "cpn-model"

logging.basicConfig(
    filename=os.getenv("SERVICE_LOG", "server.log"),
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s \
        pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
