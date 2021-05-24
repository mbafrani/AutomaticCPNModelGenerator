import logging
import os

DEBUG = os.getenv("ENVIRONMENT") == "DEV"
WAPP_APPLICATION_ROOT = os.getenv("WAPP_APPLICATION_ROOT", "/generate-cpn-model/")
API_APPLICATION_ROOT = os.getenv("API_APPLICATION_ROOT", "/api/")
HOST = os.getenv("APPLICATION_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

DATA_FOLDER = os.path.join('api', 'data')
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, 'uploads')
TEMP_FOLDER = os.path.join(DATA_FOLDER, 'tmp')
EVENT_LOG_DEFAULT_NAME = "event-log"
PROCESS_MODEL_DEFAULT_NAME = "process-model-inductive"
CPN_MODEL_DEFAULT_NAME = "cpn-model"
SML_FILE_DEFAULT_NAME = "simulate-events"

logging.basicConfig(
    filename=os.getenv("SERVICE_LOG", "server.log"),
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s \
        pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
