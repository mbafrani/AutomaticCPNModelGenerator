import logging
import os

DEBUG = os.getenv("ENVIRONMENT") == "DEV"
WAPP_APPLICATION_ROOT = os.getenv("WAPP_APPLICATION_ROOT", "/")
API_APPLICATION_ROOT = os.getenv("API_APPLICATION_ROOT", "/api/")
HOST = os.getenv("APPLICATION_HOST", "0.0.0.0")
PORT = int(os.getenv("APPLICATION_PORT", "5000"))

UPLOAD_FOLDER = os.path.join('api', 'data', 'uploads')
TEMP_FOLDER = os.path.join('api', 'data', 'tmp')
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
