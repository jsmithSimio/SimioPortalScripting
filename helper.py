# helper.py
"""
Helper functions for interacting with the Simio Portal Web API.
"""
import sys
import time
import os
import json
import pandas as pd
import itertools
import datetime

def refresh_auth_token(api, refresh_interval):
    """
    Refreshes the authentication token at regular intervals.

    :param api: The pySimio API object.
    :param refresh_interval: Time in seconds between token refreshes.
    """
    while True:
        try:
            print("Refreshing authentication token...")
            api.authenticate(personalAccessToken=os.getenv("PERSONAL_ACCESS_TOKEN"))
            print("Token refreshed successfully.")
        except Exception as e:
            print(f"Error refreshing token: {e}")
        time.sleep(refresh_interval)

def find_modelid_by_projectname(modellist_json, targetproject):
    """
    Finds the model ID by project name.

    Parameters:
        modellist (list): List of models.
        targetproject (str): Target project name.

    Returns:
        int: The model ID if found, otherwise exits.
    """
    for item in modellist_json:
        if item.get('projectName') == targetproject:
            return item.get('id')
    print(f"Model '{targetproject}' not found.")
    sys.exit()

def find_parent_run_id(json_data, run_name):
    """
    Finds the parent run ID for a given run name in the JSON data.

    Parameters:
        json_data (list): The JSON data to parse.
        run_name (str): The name of the run to search for.

    Returns:
        int: The parent run ID if found, otherwise 0.
    """
    for item in json_data:
        if item.get('name') == run_name:
            return item.get('id', 0)
    return 0

def check_run_id_status(api, experiment_id, run_id, sleep_time):
    """
    Continuously checks the status of a specific run by its run_id,
    including checking the max ID within additionalRunsStatus.

    Parameters:
        api (object): The API object used to call getRuns().
        experiment_id (int): The experiment ID to retrieve runs from.
        run_id (int): The specific run ID to check.
        sleep_time (int): The time to wait (in seconds) between status checks.

    Returns:
        None
    """
    while True:
        time.sleep(sleep_time)
        try:
            # Fetch the list of runs for the given experiment ID
            run_status_response = api.getRuns(experiment_id)

            # Print the raw response for troubleshooting
            #print("\n--- Run Status Response (JSON) ---")
            #print(json.dumps(run_status_response, indent=4))

            # Search for the parent run_id in the response
            run_status = next((run for run in run_status_response if run['id'] == run_id), None)

            # Check if the run_id was found
            if run_status is None:
                print(f"Run ID {run_id} not found in the experiment {experiment_id}.")
                break

            # Search for the child id (max ID) within additionalRunsStatus portion of JSON
            additional_runs = run_status.get('additionalRunsStatus', [])
            if additional_runs:
                # Find the run with the max ID in additionalRunsStatus
                max_additional_run = max(additional_runs, key=lambda x: x['id'])
                status = max_additional_run.get('status', 'Unknown')
                status_message = max_additional_run.get('statusMessage', '')
            else:
                # If no additional runs, use the top-level run status
                status = run_status.get('status', 'Unknown')
                status_message = run_status.get('statusMessage', '')

            # Print the current status
            if status_message:
                print(f"Status = {status}, Message = {status_message}")
            else:
                print(f"Status = {status}")

            # Continue checking if the run is still "Running" or "NotStarted"
            if status in ["Running", "NotStarted"]:
                continue
            else:
                # Run completed or failed
                if status_message:
                    print(f"Status: {status}, Message = {status_message}")
                else:
                    print(f"Done")
                break
        except Exception as e:
            print(f"Error checking run status: {str(e)}")
            break

def get_parent_experiment_id(data, project_name, run_name=None):
    # Retrieves the experiment ID for a given project name from the JSON dataset.
    #
    # Parameters:
    #     data (list): A list of dictionaries representing JSON data.
    #     project_name (str): The name of the project to find the experiment ID for.
    #     run_name (str): The (optional) name of the run associated wih the experiment
    #
    # Returns:
    #     int or None: The experiment ID if found, otherwise None.
    for entry in data:
        if entry.get("projectName") == project_name:
            if run_name is None:
                return entry.get("experimentId")
            elif entry.get("name") == run_name:
                return entry.get("experimentId")
    return None  # Return None if no match is found

def find_id_by_model_id(data, model_id):
    """
    Finds and returns the `id` value from a list of dictionaries given a `modelId`.

    Parameters:
        data (list): List of dictionaries containing 'id' and 'modelId' keys.
        model_id (str): The modelId to search for.

    Returns:
        int or None: The corresponding id if found, otherwise None.
    """
    for item in data:
        if item.get("modelId") == model_id:
            return item.get("id")
    return None

def get_id_by_experiment_and_name(data, experiment_id, name):
    """
    Returns the `id` of the object that matches the given experimentId and name.

    Parameters:
        data (list): A list of dictionaries representing experiment runs.
        experiment_id (int): The experimentId to search for.
        name (str): The name to search for.

    Returns:
        int or None: The matching id if found, otherwise None.
    """
    for item in data:
        if item.get("experimentId") == experiment_id and item.get("name") == name:
            return item.get("id")
    return None

def wait_for_run(api, run_id, sleep_time, max_cycles, show=True):
    """
    Continuously checks the status of a specific run by its run_id and
    returns when the run status is not "Running" or "NotStarted"

    Parameters:
        api (object): The API object used to call getRuns().
        run_id (int): The specific run ID to check.
        sleep_time (int): The time to wait (in seconds) between status checks.
        max_cycles (int): The maximum number of cycles to wait
        show (Boolean): If True, prints status; otherwise, silent.

    Returns:
        2-item list -- status, number of cycles
    """
    try: 
        for cycle in range(max_cycles):
            time.sleep(sleep_time)
            status = api.getRun(run_id)['status']
            if show:
                print(f"Status for cycle {cycle+1}: {status}")
            if status not in ["Running", "NotStarted", "Pending"]:
                break
        if show:
            print(f"Exiting after {cycle+1} cycles with status {status}")
        return [status, cycle+1]
    except Exception as e:
        print(f"Error checking run status: {str(e)}")
        return None

def scenario_results_as_df(scenarios):
    """
    Convert simulation experiment JSON to a pandas DataFrame.
    
    Parameters:
    -----------
    scenarios : str, dict, or list
        Either a JSON string, a dictionary, or a list of scenario dictionaries
        
    Returns:
    --------
    pd.DataFrame
        DataFrame where each row is a scenario, with columns for:
        - scenarioName
        - Each control value
        - Each response average
    """
    # Handle different input types
    if isinstance(scenarios, str):
        data = json.loads(scenarios)
    else:
        data = scenarios
    
    # List to store each scenario's data
    rows = []
    responses = set()
    controls = set()
    for scenario in data:
        # Start with scenario name
        row = {'scenarioName': scenario['scenarioName']}
        
        # Add response averages
        for response in scenario['responseValues']:
            responses.add(response['name'])
            row[response['name']] = response['average']
            row[f"{response['name']}-h"] = response['halfWidth']

        # Add control values
        for control in scenario['controlValues']:
            controls.add(control['name'])
            # Convert value to appropriate type (numeric if possible)
            try:
                row[control['name']] = float(control['value'])
            except ValueError:
                row[control['name']] = control['value']
        
        rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    responses = list(responses)
    controls = list(controls)
    return df, responses, controls

def create_ff_experiment(experiment_id, run_name, num_reps, vars):
    """
    Creates the JSON representation of an experiment run based on a full factorial
    design of the variables
    
    Parameters:
        experiment_id - Experiment ID
        run_name - Run name
        num_reps - Number of replications for each scenario
        vars - Variable levels. Example:
            vars = {
    	        "x" : [2, 4, 6],
	            "y" : [1, 2, 3, 4, 5],
	            "z" : [1, 2, 3]
            }
    Returns:
        List of dictionaries of the form: {'x': 2, 'y': 1, 'z': 1, 'q': 7}
    """
    
    # Extract the variable names in order
    var_names = list(vars.keys())
    # Extract the list of levels for each variable
    level_lists = [vars[var] for var in var_names]
    # Compute the Cartesian product
    product = itertools.product(*level_lists)
    # Convert each combination to a dictionary
    design = [dict(zip(var_names, combination)) for combination in product]

    scenarios = []
    current_dp = 1
    for dp in design:
        control_values = []
        for var in dp:
            control_values.append({"Name": var, "Value": str(dp[var])})

        scenarios.append({
            "Name"                 : f"Secenario{current_dp}",
            "ReplicationsRequired" : num_reps,
            "ControlValues"        : control_values
        })
        current_dp += 1

    experiment = {
        "ExperimentID" : experiment_id,
        "Name"         : run_name,
        "CreateInfo"   : {"Scenarios" : scenarios}
    }

    return experiment

def scenarios_to_dataframe(scenarios):
    """
    Creates a Pandas dataframe from the scenarions defined for an experiment
    
    Parameters:
        scenarios json from an experiment - usually j["CreateInfo"]["Scenarios"],
        if j is an experiment payload

    Returns:
        Pandas dataframe
    """
    def try_cast(value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value  # leave as-is if not numeric

    records = []
    for scenario in scenarios:
        row = {
            "scenarioName": scenario["Name"],
            "Reps": scenario["ReplicationsRequired"]
        }
        for control in scenario["ControlValues"]:
            row[control["Name"]] = try_cast(control["Value"])
        records.append(row)

    df = pd.DataFrame(records)
    df.set_index("scenarioName", inplace=True)
    return df

def get_runs_for_experiment(api, experiment_id):
    """
    Finds all existing runs for the given experiment (experiment_id)

    Returns: List of runs for the experiment
    """
    all_runs = api.getRuns()
    runs = []
    for item in all_runs:
        if item.get('experimentId') == experiment_id:
            runs.append(item.get('id'))
    return runs

def delete_runs(api, runs):
    """
    Deletes the runs in the list
    """
    for run_id in runs:
        api.deleteRun(run_id)

def get_run(api, run_id, showStatus = True):
    theRun = None
    try: 
        theRun = api.getRun(run_id)
        if showStatus:
            status = theRun['status']
            completedReps = theRun['completedReplications']
            totalReps = theRun['totalReplications']
            # Get the current date and time
            current_time_local = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            print(f"Status of run {run_id} at {current_time_local}: {status} ({completedReps}/{totalReps})")
    except Exception as e:
        print(f"Error checking run status: {str(e)}")
    return theRun


