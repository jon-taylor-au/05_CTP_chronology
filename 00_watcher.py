## REMEMBER!! Start the windows task scheduler task "CTP Watcher" to run this script ##
import hashlib
import time
import subprocess
from datetime import datetime

WATCH_FILE = r"\\V0050\05_CTP_chronology\00_courtbooks_to_get.csv"
SCRIPT_TO_RUN = r"\\V0050\05_CTP_chronology\07_main.py"
WATCHER_LOG = r"\\V0050\05_CTP_chronology\watcher.log"
SCRIPT_LOG = r"\\V0050\05_CTP_chronology\07_main.log"
PROGRESS_LOG = r"\\V0050\05_CTP_chronology\run_scripts\progress.log"
POLL_INTERVAL = 60  # seconds

def log_progress(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

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

        # Clear progress log at the start
    with open(PROGRESS_LOG, "w", encoding="utf-8") as f:
        f.write("")
        
    log_progress("Watcher service started and monitoring file.")
    print(f"Watching for changes to: {WATCH_FILE}")
    last_hash = file_hash(WATCH_FILE)
    while True:
        time.sleep(POLL_INTERVAL)
        current_hash = file_hash(WATCH_FILE)
        if current_hash and current_hash != last_hash:
            log("Change detected. Launching script.")
            log_progress("Change detected in watch file. Starting script.")
            try:
                log("Running 07_main.py (output -> 07_main.log)")
                log_progress("Running main processing script.")
                with open(SCRIPT_LOG, "a", encoding="utf-8") as log_target:
                    subprocess.Popen(
                        ["python", SCRIPT_TO_RUN],
                        stdout=log_target,
                        stderr=log_target
                    )
                log("Script started successfully.")
                log_progress("Script launched successfully.")
            except Exception as e:
                log(f"Error starting script: {e}")
                log_progress(f"ERROR: Could not start script - {e}")
            last_hash = current_hash


if __name__ == "__main__":
    watcher()
