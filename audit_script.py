import os, re, csv
from datetime import datetime
import pandas as pd

# This evaluates start / stop times

with open('petref.csv', 'r') as f:
    reader = csv.reader(f)
    tracer_protocols = list(reader)

df = pd.read_csv('pet_2024.csv')

# helper function to match tracers
def find_index_for_tracer(file_path, target_tracer):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['tracer_name'] == target_tracer:
                return int(row['index'])
    return None

def compare_times(data):
    # add results column
    data["results"] = ""
    # code requires specific column names: injection_time, scan_time, tracer
    for i, (inject_t, scan_t, tracer) in enumerate(zip(data['injection_time'], data['scan_time'], data['tracer'])):
        # regular expression for gathering the scan injection and start time
        injection_time = re.findall('(\d{1,2}:\d{1,2}:\d{1,2})', inject_t)
        scan_time = re.findall('(\d{1,2}:\d{1,2}:\d{1,2})', scan_t)
        
        if injection_time and scan_time:  # check if both times are not empty
            injection_time_obj = datetime.strptime(injection_time[0], "%H:%M:%S")
            scan_time_obj = datetime.strptime(scan_time[0], "%H:%M:%S")
            time_difference = scan_time_obj - injection_time_obj
            delta = round(time_difference.total_seconds() / 60.0)
            index = find_index_for_tracer('petref.csv', f'{tracer}') # manipulate the index vlaue for the tracer
            
            if index is not None:
                # pull lines based on selection
                selection = int(index)
                tracer_name = tracer_protocols[selection][1]
                desired_static_delay = tracer_protocols[selection][2]
                desired_dynamic_delay = tracer_protocols[selection][3]
                mst = tracer_protocols[selection][4]
                mdt = tracer_protocols[selection][5]
                model_state_if_dynamic = tracer_protocols[selection][6]
                model_state_if_static = tracer_protocols[selection][7]
                static_minimum = tracer_protocols[selection][8]
                static_maximum = tracer_protocols[selection][9]
                dynamic_minimum = tracer_protocols[selection][10]
                dynamic_maximum = tracer_protocols[selection][11]
                
            try:
                optimal = None
                # if optimal
                # Optimal dynamic
                if delta == int(desired_dynamic_delay):
                    result = f"{delta} is optimal for {tracer_name} (dynamic: {model_state_if_dynamic})"
                    optimal = True
                # Optimal static
                if delta == int(desired_static_delay):
                    result = f"{delta} is optimal for {tracer_name} (static: {model_state_if_static})"
                    optimal = True

                # if sub-optimal
                if not optimal:
                    # Sub-optimal dynamic
                    if delta in range(int(dynamic_minimum), int(dynamic_maximum)+1):
                        result = f"{delta} is sub-optimal for {tracer_name} (dynamic: {model_state_if_dynamic})"
                    # Sub-optimal static
                    if delta in range(int(static_minimum), int(static_maximum)+1):
                        result = f"{delta} is sub-optimal for {tracer_name} (static: {model_state_if_static})"

                # if unacceptable
                if not optimal:
                    # Unacceptable dynamic
                    if delta > int(dynamic_maximum) and delta < int(static_minimum):
                        result = f"{delta} is beyond tolerance for {tracer_name} (dynamic: {model_state_if_dynamic})"
                    # Unacceptable static
                    if delta > int(static_maximum):
                        result = f"{delta} is beyond tolerance for {tracer_name} (static: {model_state_if_static})"

            except (IndexError,ValueError,KeyError):
                result = "No Parse"
            data.at[i, 'results'] = result # add result to results column
            
compare_times(df)
df.to_csv('audit_result.csv')