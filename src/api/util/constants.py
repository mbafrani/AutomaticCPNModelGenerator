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
DICT_KEY_ARRIVAL_RATE = "arrivalrate"
DICT_KEY_PERF_RES_CAP = "resource_capacity"
DICT_KEY_TRANS_INDEX_PETRI = "TRANSITION_INDEX_INFORMATION_PETRI"
DICT_KEY_TRANS_NAMES = "transition_names"
DICT_KEY_RESOURCE_POOLING = "resource_pools"
DICT_KEY_RESOURCE_TRANS = "activities"
DICT_KEY_RESOURCE_NAMES = "resources"
DICT_KEY_RESOURCE_CAP = "capacity"

# default performance values
PERF_MEAN_DEFAULT_VALUE = 0.0
PERF_STDEV_DEFAULT_VALUE = 0.0
PERF_RES_CAP_VALID_TRANS_DEFAULT_VALUE = 1
PERF_RES_CAP_SILENT_TRANS_VALUE = 0

# declaration constants
DECLARATION_COLOR_CASE_ID = "CASE_ID"
DECLARATION_COLOR_CASE_ID_DATATYPE = "int"
DECLARATION_COLOR_CASE_ID_VARIABLE = "c"
DECLARATION_COLOR_PROBABILITY = "INT"
DECLARATION_COLOR_PROBABILITY_DATATYPE = "int"
DECLARATION_COLOR_PROBABILITY_VARIABLE = "p"
DECLARATION_COLOR_PROBABILITY_FUNCTION = "discrete(0, 99)"
DECLARATION_COLOR_RES_CAPACITY = "R"
DECLARATION_COLOR_RES_CAPACITY_DATATYPE = "enum"
DECLARATION_COLOR_RES_CAPACITY_VARIABLE = "r"
DECLARATION_COLOR_OPEN_EL_TYPE = "INT"
DECLARATION_COLOR_EXP_DISTRIB_FUNCTION = "fun Exp(arrival_rate) = round(exponential(1.0/arrival_rate));"
DECLARATION_COLOR_NORMAL_DISTRIB_FUNCTION = "fun N(mean, stddev) = normal(mean, stddev);"
DECLARATION_BLOCK_EXEC_TIME_ID = "Transition Exec Times"
DECLARATION_VAR_EXEC_TIME = "execTime_{0}"
DECLARATION_ASSIGNMENT_EXEC_TIME = "val " + DECLARATION_VAR_EXEC_TIME + " = ref 0;"
DECLARATION_CODE_SEGMENT_EXEC_TIME = "action ({0} := {1})"
DECLARATION_CODE_SEGMENT_INPUT = f"input({DECLARATION_COLOR_CASE_ID_VARIABLE})"
DECLARATION_CODE_SEGMENT_ACTION = "action\n" \
                                  "{0} := round(event(" + DECLARATION_COLOR_CASE_ID_VARIABLE + ", \"{1}\", \"{2}\", {3}))"
DECLARATION_CODE_SEGMENT_OPEN_FILE = "input();\n output();\n action\n (create_log_file(attr));"

# cpn model places colors
CPN_MODEL_PLACE_DEFAULT_FILL_COLOR = "White"
CPN_MODEL_PLACE_DEFAULT_LINE_COLOR = "Black"
CPN_MODEL_PLACE_DEFAULT_TEXT_COLOR = "Black"

CPN_MODEL_PLACE_SOURCE_FILL_COLOR = "Teal"
CPN_MODEL_PLACE_SOURCE_LINE_COLOR = "Black"
CPN_MODEL_PLACE_SOURCE_TEXT_COLOR = "White"

CPN_MODEL_PLACE_SINK_FILL_COLOR = "Blue"
CPN_MODEL_PLACE_SINK_LINE_COLOR = "Black"
CPN_MODEL_PLACE_SINK_TEXT_COLOR = "White"

CPN_MODEL_PLACE_NEXT_CASE_ID_FILL_COLOR = "White"
CPN_MODEL_PLACE_NEXT_CASE_ID_LINE_COLOR = "Green"
CPN_MODEL_PLACE_NEXT_CASE_ID_TEXT_COLOR = "Green"

CPN_MODEL_PLACE_OPEN_EL_FILL_COLOR = "White"
CPN_MODEL_PLACE_OPEN_EL_LINE_COLOR = "Black"
CPN_MODEL_PLACE_OPEN_EL_TEXT_COLOR = "Black"

CPN_MODEL_PLACE_DECISION_PROB_FILL_COLOR = "White"
CPN_MODEL_PLACE_DECISION_PROB_LINE_COLOR = "Green"
CPN_MODEL_PLACE_DECISION_PROB_TEXT_COLOR = "Green"

CPN_MODEL_PLACE_RES_CAP_FILL_COLOR = "White"
CPN_MODEL_PLACE_RES_CAP_LINE_COLOR = "Green"
CPN_MODEL_PLACE_RES_CAP_TEXT_COLOR = "Green"

# cpn model transition colors
CPN_MODEL_TRANS_DEFAULT_FILL_COLOR = "Silver"
CPN_MODEL_TRANS_OPEN_FILE_FILL_COLOR = "White"
CPN_MODEL_TRANS_DEFAULT_LINE_COLOR = "Black"
CPN_MODEL_TRANS_DEFAULT_TEXT_COLOR = "Black"

# cpn model arc colors
CPN_MODEL_ARC_DEFAULT_LINE_COLOR = "Black"
CPN_MODEL_ARC_DEFAULT_ANNOT_TEXT_COLOR = "Teal"

CPN_MODEL_ARC_NEXT_CASE_ID_LINE_COLOR = "Green"
CPN_MODEL_ARC_NEXT_CASE_ID_ANNOT_TEXT_COLOR = "Green"

CPN_MODEL_ARC_DECISION_PROB_LINE_COLOR = "Green"
CPN_MODEL_ARC_DECISION_PROB_ANNOT_TEXT_COLOR = "Green"

CPN_MODEL_ARC_RES_CAP_LINE_COLOR = "Green"
CPN_MODEL_ARC_RES_CAP_ANNOT_TEXT_COLOR = "Green"


# orientation constants
PLACE_TO_TRANS_ORIENTATION = "PtoT"
TRANS_TO_PLACE_ORIENTATION = "TtoP"

# place name constants
PLACE_NAME_SOURCE = "source"
PLACE_NAME_SINK = "sink"


class PetriNetDictKeys:
    net = "net"
    frequencies = "successor_frequencies"
    performance = DICT_KEY_PERF_INFO_PETRI
    mean = DICT_KEY_PERF_MEAN
    std = DICT_KEY_PERF_STDEV
    arrivalrate = DICT_KEY_ARRIVAL_RATE
    places = "places"
    transitions = "transitions"
    transition_names = "transition_names"
    res_capacity = "resource_capacity"


class RequestJsonKeys:
    event_log_id = "event_log_id"
    place = "place"
    frequencies = "frequencies"
    arrivalrate = "arrivalrate"
    transitions = "transitions"
    transition = "transition"
    mean = "mean"
    std = "std"
    res_capacity = "resource_capacity"
