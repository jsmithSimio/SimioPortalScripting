#
# Creates and executes a run
#
# Imports - Make sure to delete the __pycache__ directory and restart the kernel if you change helper.py.
from helper import *
from pysimio import pySimio
from dotenv import load_dotenv
import os
import threading
from pysimio.classes import TimeOptions
import datetime
import pandas as pd

#
# Model-specific Data
#
model_id = 141
experiment_id = 221
run_name = "API01"
# For sorting the scenarios after the run
sort_response = "Throughput"
sort_ascending = False
# Create the json experiment payload
# Careful - code will create all combinations of these values
vars = {
    "Buff1" : [2, 3],
    "Buff2" : [2, 3],
    "Buff3" : [2, 3],
    "CapA"  : [2, 3, 4],
    "CapB"  : [2, 3, 4],
    "CapC"  : [2, 3, 4],
    "CapD"  : [2, 3, 4]
}
num_reps = 6
experiment_def = create_ff_experiment(experiment_id, run_name, num_reps, vars)
n = len(experiment_def["CreateInfo"]["Scenarios"])
print(f"Experiment {experiment_def["Name"]} has {n} scenarios and {n*num_reps} total replications.")

#
# Connect to Portal and create/execute run
#
# Load environment variables
# Makes sure that .env is set up for the portal instance that you want.
load_dotenv(override=True)
simio_portal_url = os.getenv("SIMIO_PORTAL_URL")
print(f"Connecting to portal on: {simio_portal_url}")
personal_access_token = os.getenv("PERSONAL_ACCESS_TOKEN")
auth_refresh_time = 500  # Time in seconds to refresh the auth token
run_status_refresh_time = 10
# Ensure token is loaded
if not personal_access_token:
    raise ValueError("Personal access token not found. Make sure it's set in the environment.")

# API Initialization getting bearer token for authorization
api = pySimio(simio_portal_url)
api.authenticate(personalAccessToken=personal_access_token)

# Start token refresh in a background thread
threading.Thread(target=refresh_auth_token, args=(api, auth_refresh_time), daemon=True).start()

# Run the experiment.
run_id = api.startRun(experiment_def)
# Get the current date and time
current_time_local = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"Started run {run_name} ({run_id}) with {len(experiment_def["CreateInfo"]["Scenarios"])} scenarios at {current_time_local}.")
theRun = get_run(api, run_id, True)
sleep_time = 10 # seconds
status = wait_for_run(api, run_id, sleep_time, 2000, False)
theRun = get_run(api, run_id, True)
print(f"Final run status after approx. {status[1]*sleep_time/60:.2f} minutes ({status[1]} cycles): {status[0]}")
#
# Get the experiment response results
#
rows_to_show = 5
scenarios = api.getScenarios(run_id = run_id)
# Convert to dataframe
df, responses, controls = scenario_results_as_df(scenarios)
# remove any scenarios with non-numeric values in the sort column
df[sort_response] = pd.to_numeric(df[sort_response], errors='coerce')
df_cleaned = df.dropna(subset=[sort_response])
if len(df) > len (df_cleaned):
    print(f"Removed {len(df)-len(df_cleaned)} rows with non-numeric values in the sort column.")
print(f"Dataframe from run_id {run_id} includes {len(df_cleaned)} scenarios.")
# --- Display the Table ---
print(f"--- Top (up to) {rows_to_show} Scenario Response Averages by {sort_response} ---")
df_sorted = df_cleaned.sort_values(by=sort_response, ascending=sort_ascending)
print(df_sorted[:rows_to_show].to_string())
