import csv
import subprocess
import os
import sys
from datetime import datetime

PROGRESS_LOG = r"\\V0050\05_CTP_chronology\run_scripts\progress.log"

def log_progress(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

csv_path = r"\\V0050\05_CTP_chronology\00_courtbooks_to_get.csv"

with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
    reader = list(csv.reader(f))

if len(reader) < 1:
    log_progress("ERROR: CSV is missing data. Aborting.")
    print("CSV is missing data.")
    exit()

log_progress("New entry detected in CSV. Starting processing pipeline.")
print("New value detected running scripts...")

print("Step 1: Extracting data and saving as csv")
log_progress("Step 1: Extracting data...")

try:
    subprocess.run(["python", "01_webapp_extract_data.py"], check=True, timeout=30)
except subprocess.TimeoutExpired:
    log_progress("ERROR: Step 1 timed out after 30 seconds.")
    print("ERROR: Step 1 (data extraction) timed out.")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    log_progress(f"ERROR: Step 1 failed with return code {e.returncode}.")
    print(f"ERROR: Step 1 (data extraction) failed.")
    sys.exit(1)


print("Step 2: Generating chronologies in chunks then merging")
log_progress("Step 2: Generating chronologies...")
subprocess.run(["python", "02_chronology_generate.py"], check=True)

print("Step 3: Post processing the data")
log_progress("Step 3: Post-processing data...")
subprocess.run(["python", "03_post_process.py"], check=True)

print("Step 4: Build the writeback payload")
log_progress("Step 4: Creating writeback payload...")
subprocess.run(["python", "04_create_payload.py"], check=True)

print("Step 5: Writing back...")
log_progress("Step 5: Writing data back...")
subprocess.run(["python", "05_writeback.py"], check=True)

print("Step 6: Cleanup and finish")
log_progress("Step 6: Performing cleanup...")
subprocess.run(["python", "06_cleanup.py"], check=True)

print("All done.")
log_progress("Processing complete.")
