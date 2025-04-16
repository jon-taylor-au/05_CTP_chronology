import os
import json
import pandas as pd
import csv
from supporting_files.webapp_class import APIClient

# Constants
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
OUTPUT_LOCATION = "outputs/"
CSV_FILE = "00_courtbooks_to_get.csv"

def load_json(filename):
    try:
        with open(os.path.join(OUTPUT_LOCATION, filename), "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def send_put_request(client, court_book_id, json_data):
    url = f"/sparke/api/v0/books/{court_book_id}/chronology/"
    response = client.send_put_request(url, json_data)
    if response.status_code == 200:
        print(f"Updated Court Book ID: {court_book_id}")
    else:
        print(f"Failed to update {court_book_id}. Status: {response.status_code}")

def main():
    client = APIClient(BASE_URL, LOGIN_PAGE_URL, LOGIN_URL)
    if not client.authenticate():
        print("Authentication failed. Exiting.")
        return

    with open(CSV_FILE, newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header

        for row in reader:
            if not row or not row[0].strip():
                continue

            court_book_id = row[0].strip()
            payload_filename = f"{court_book_id}_payload.json"
            payload_data = load_json(payload_filename)

            if not payload_data:
                print(f"No data to send for Court Book ID: {court_book_id}")
                continue

            send_put_request(client, court_book_id, payload_data)


    # Exclusion list (e.g. "22672","22680","22648")
    excluded_ids = [] 
    
    # Filter out excluded records
    original_count = len(payload_data)
    filtered_payload = [entry for entry in payload_data if str(entry.get("id")) not in excluded_ids]
    removed_count = original_count - len(filtered_payload)

    print(f"Payload loaded: {original_count} records")
    print(f"Excluded {removed_count} record(s) based on ID filter")
    
    if not filtered_payload:
        print("All records were excluded — nothing to upload.")
        return

    send_put_request(client, court_book_id, filtered_payload)


if __name__ == "__main__":
    main()