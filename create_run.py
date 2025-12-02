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

#
# Model-specific Data
#
model_id = 129
experiment_id = 206
run_name = "API01"
# For sorting the scenarios after the run
sort_response = "Throughput"
sort_ascending = False
# Create the json experiment payload
vars = {
    "Buff1" : [3],
    "Buff2" : [3],
    "Buff3" : [3],
    "CapA"  : [2, 4],
    "CapB"  : [2, 4],
    "CapC"  : [2, 4],
    "CapD"  : [2, 4]
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

