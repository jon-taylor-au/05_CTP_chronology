import csv
import subprocess
import os
import sys

# Set working directory to script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#11602

#csv_path = "00_courtbooks_to_get.csv"
csv_path = r"\\V0050\05_CTP_chronology\00_courtbooks_to_get.csv"

# Read the CSV
with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
    reader = list(csv.reader(f))

# Check header and first row
if len(reader) < 1:
    print("CSV is missing data.")
    exit()

header = reader[0]
row = reader[1]

print("New value detected running scripts...")

print("Step 1: Extracting data and saving as csv")
subprocess.run(["python", "01_webapp_extract_data.py"], check=True)

print("Step 2: Generating chronologies in chunks then merging")
subprocess.run(["python", "02_chronology_generate.py"], check=True)

print("Step 3: Post processing the data")
subprocess.run(["python", "03_post_process.py"], check=True)

print("Step 4: Build the writeback payload")
subprocess.run(["python", "04_create_payload.py"], check=True)

print("Step5: Writing back...")
#subprocess.run(["python", "05_writeback.py"], check=True)

print("Step 6: Cleanup and finish")
subprocess.run(["python", "06_cleanup.py"], check=True)

print("All done.")
