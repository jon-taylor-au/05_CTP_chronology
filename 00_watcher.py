## REMEMBER!! Start the windows task scheduler task "CTP Watcher" to run this script ##
import hashlib
import time
import subprocess
from datetime import datetime

WATCH_FILE = r"\\V0050\05_CTP_chronology\00_courtbooks_to_get.csv"
SCRIPT_TO_RUN = r"\\V0050\05_CTP_chronology\07_main.py"
WATCHER_LOG = r"\\V0050\05_CTP_chronology\watcher.log"
SCRIPT_LOG = r"\\V0050\05_CTP_chronology\07_main.log"
POLL_INTERVAL = 15  # seconds

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(WATCHER_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def watcher():
    log("Watcher started.")
    print(f"Watching for changes to: {WATCH_FILE}")
    last_hash = file_hash(WATCH_FILE)
    while True:
        time.sleep(POLL_INTERVAL)
        current_hash = file_hash(WATCH_FILE)
        if current_hash and current_hash != last_hash:
            log("Change detected. Launching script.")
            try:
                log("Running 07_main.py (output -> 07_main.log)")
                with open(SCRIPT_LOG, "a", encoding="utf-8") as log_target:
                    subprocess.Popen(
                        ["python", SCRIPT_TO_RUN],
                        stdout=log_target,
                        stderr=log_target
                    )
                log("Script started successfully.")
            except Exception as e:
                log(f"Error starting script: {e}")
            last_hash = current_hash

if __name__ == "__main__":
    watcher()
