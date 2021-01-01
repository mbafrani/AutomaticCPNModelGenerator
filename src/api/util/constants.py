# Error messages
ERROR_FILE_NOT_FOUND_IN_REQUEST = "'file' not found in request body"
ERROR_INVALID_FILE = "Invalid file"
ERROR_EVENT_LOG_ID_NOT_FOUND_IN_REQUEST = "'event_log_id' not found in request body"
ERROR_EVENT_LOG_DOESNT_EXIST = "An event log with the provided ID does not exist."
ERROR_MISSING_PARAMETER_PERFORMANCE = "One of the parameters 'transition', 'mean', or 'std' is missing."
ERROR_MISSING_PARAMETER_FREQUENCY = "One of the parameters 'place', 'frequencies' is missing."

# Messages
MESSAGE_EVENT_LOG_UPLOAD_SUCCESS = "Event log uploaded successfully"

# File extension constants
XES_EXTENSION = "xes"
CSV_EXTENSION = "csv"
ALLOWED_EXTENSIONS = {XES_EXTENSION, CSV_EXTENSION}

# dictionary keys
DICT_KEY_OBJECTS_CONSTANT = "objects"
DICT_KEY_EDGES_CONSTANT = "edges"
DICT_KEY_LAYOUT_INFO_PETRI = "LAYOUT_INFORMATION_PETRI"
DICT_KEY_LAYOUT_X = "x"
DICT_KEY_LAYOUT_Y = "y"
DICT_KEY_LAYOUT_HEIGHT = "height"
DICT_KEY_LAYOUT_WIDTH = "width"
DICT_KEY_PERF_INFO_PETRI = "PERFORMANCE_INFORMATION_PETRI"
DICT_KEY_PERF_MEAN = "mean"
DICT_KEY_PERF_STDEV = "stdev"
DICT_KEY_PROBA_INFO_PETRI = "DECISION_PROBABILITY_INFORMATION_PETRI"
DICT_KEY_FREQUENCY = "successor_frequencies"
DICT_KEY_PLACE_PROB_INDEX = "DICT_KEY_PLACE_PROB_INDEX"
DICT_KEY_ARRIVAL_RATE = "arrivalrate"

# default performance values
PERF_MEAN_DEFAULT_VALUE = 0.0
PERF_STDEV_DEFAULT_VALUE = 0.0

# declaration constants
DECLARATION_COLOR_CASE_ID = "CASE_ID"
DECLARATION_COLOR_CASE_ID_DATATYPE = "int"
DECLARATION_COLOR_CASE_ID_VARIABLE = "c"
DECLARATION_COLOR_PROBABILITY = "INT"
DECLARATION_COLOR_PROBABILITY_DATATYPE = "int"
DECLARATION_COLOR_PROBABILITY_VARIABLE = "p"
DECLARATION_COLOR_PROBABILITY_FUNCTION = "discrete(0, 99)"

# orientation constants
PLACE_TO_TRANS_ORIENTATION = "PtoT"
TRANS_TO_PLACE_ORIENTATION = "TtoP"


class PetriNetDictKeys:
    net = "net"
    frequencies = "successor_frequencies"
    performance = DICT_KEY_PERF_INFO_PETRI
    mean = DICT_KEY_PERF_MEAN
    std = DICT_KEY_PERF_STDEV
    arrivalrate = DICT_KEY_ARRIVAL_RATE
    places = "places"
    transitions = "transitions"


class RequestJsonKeys:
    event_log_id = "event_log_id"
    place = "place"
    frequencies = "frequencies"
    arrivalrate = "arrivalrate"
    transitions = "transitions"
    transition = "transition"
    mean = "mean"
    std = "std"
