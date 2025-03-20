import os
import json
import csv
import pandas as pd
from supporting_files.webapp_class import APIClient
from bs4 import BeautifulSoup

# Constants
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = "00_courtbooks_to_get.csv"
OUTPUT_LOCATION = "outputs/"

def save_json(data, filename):
    """Saves JSON data to a file."""
    with open(os.path.join(OUTPUT_LOCATION, filename), "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"✅ JSON file saved: {filename}")

def load_json(filename):
    """Loads JSON data from a file."""
    try:
        with open(os.path.join(OUTPUT_LOCATION, filename), "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"⚠️ Error loading {filename}: {e}")
        return []

def fetch_court_book_data(client, court_book_id):
    """Fetches court book chronology data from the API."""
    response = client.fetch_api_data(f"/sparke/api/v0/books/{court_book_id}/chronology/")
    if response:
        save_json(response, f"{court_book_id}_source_extract.json")
    else:
        print(f"⚠️ No data found for Court Book ID: {court_book_id}")

def format_response(response, source_doc):
    """Formats the response text."""
    if not isinstance(response, str) or not response.strip():
        return ""
    lines = response.replace("\t", "").split("\n")
    lines = [line.strip() for line in lines if line.strip()]
    lines[0] = f"{source_doc}:"
    return "\n".join([line for line in lines if line.lower() != "ai summary"]).strip()

def merge_json_data(source_data, response_data):
    """Merges source data with response data."""
    response_dict = {item["LineID"]: item["Response"] for item in response_data}
    for entry in source_data:
        entry_id = str(entry["id"])
        if entry_id in response_dict:
            entry["entryFinal"] = response_dict[entry_id]
    return source_data

def process_court_book(client, court_book_id):
    """Handles full processing for a court book ID."""
    fetch_court_book_data(client, court_book_id)
    input_xlsx = f"outputs/{court_book_id}_chronology.xlsx"
    output_json = f"{court_book_id}_response_extract.json"
    
    try:
        df = pd.read_excel(input_xlsx, dtype=str)
        required_columns = {"Response", "LineID", "Source Doc"}
        if not required_columns.issubset(df.columns):
            print(f"⚠️ Missing required columns in {input_xlsx}")
            return
        df["Response"] = df.apply(lambda row: format_response(row["Response"], row["Source Doc"]), axis=1)
        extracted_df = df[["LineID", "Response"]]
        save_json(extracted_df.to_dict(orient="records"), output_json)
    except Exception as e:
        print(f"⚠️ Error processing {input_xlsx}: {e}")
    
    source_data = load_json(f"{court_book_id}_source_extract.json")
    response_data = load_json(f"{court_book_id}_response_extract.json")
    merged_data = merge_json_data(source_data, response_data)
    save_json(merged_data, f"{court_book_id}_payload.json")
    send_put_request(client, court_book_id, merged_data)

def send_put_request(client, court_book_id, json_data):
    """Asks for confirmation before sending a PUT request to update the court book."""
    confirm = input(f"⚠️ >> About to overwrite data for Court Book ID {court_book_id}. Are you sure you want to proceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Operation cancelled by user.")
        return
    """Sends a PUT request to update the court book."""
    url = f"/sparke/api/v0/books/{court_book_id}/chronology/"
    response = client.send_put_request(url, json_data)
    if response.status_code == 200:
        print(f"✅ Successfully updated Court Book ID: {court_book_id}")
    else:
        print(f"❌ Failed to update Court Book ID: {court_book_id}. Status: {response.status_code}")

def main():
    """Main function to handle all court books from the CSV file."""
    client = APIClient(BASE_URL, LOGIN_PAGE_URL, LOGIN_URL)
    if not client.authenticate():
        print("❌ Authentication failed. Exiting.")
        return
    with open(CSV_FILE, newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            for court_book_id in row:
                process_court_book(client, court_book_id.strip())

if __name__ == "__main__":
    main()
