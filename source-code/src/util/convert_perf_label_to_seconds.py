import re

# retrive time information from performance labels and convert them to seconds
# egs of performance labels: 0s (seconds), 20m (minutes), 18h (hours), 5D (Days)
def convert_perf_label_to_seconds(perf_label):
    if(perf_label == ""):
        return None
    
    perf_regex = re.compile("([0-9]+)([a-zA-Z]+)")
    perf_matches = perf_regex.match(perf_label)
    
    perf_number = perf_matches.group(1)
    perf_str = perf_matches.group(2)
    
    if (perf_str == "s"):
        return int(perf_number)
    elif (perf_str == "m"):
        return int(perf_number) * 60 # seconds = minutes * 60
    elif (perf_str == "h"):
        return int(perf_number) * 3600 # seconds = hours * 3600
    elif (perf_str == "D"):
        return int(perf_number) * 86400 # seconds = days * 86400
    else:
        return None
