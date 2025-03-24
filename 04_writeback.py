import os
import json
import pandas as pd
from supporting_files.webapp_class import APIClient

# Constants
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
OUTPUT_LOCATION = "outputs/"

def load_json(filename):
    try:
        with open(os.path.join(OUTPUT_LOCATION, filename), "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"⚠️ Error loading {filename}: {e}")
        return []

def send_put_request(client, court_book_id, json_data):
    confirm = input(f"⚠️ >> Overwrite data for Court Book ID {court_book_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        return

    url = f"/sparke/api/v0/books/{court_book_id}/chronology/"
    response = client.send_put_request(url, json_data)
    if response.status_code == 200:
        print(f"✅ Updated Court Book ID: {court_book_id}")
    else:
        print(f"❌ Failed to update {court_book_id}. Status: {response.status_code}")

def main():
    client = APIClient(BASE_URL, LOGIN_PAGE_URL, LOGIN_URL)
    if not client.authenticate():
        print("❌ Authentication failed. Exiting.")
        return

    court_book_id = input("Enter Court Book ID to upload: ").strip()
    payload_filename = f"{court_book_id}_payload.json"
    payload_data = load_json(payload_filename)

    if not payload_data:
        print("❌ No data to send.")
        return

    send_put_request(client, court_book_id, payload_data)

if __name__ == "__main__":
    main()