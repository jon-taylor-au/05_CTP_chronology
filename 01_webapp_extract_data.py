
""" Endpoints available for the API:
sydwebdev139:8080/sparke/api/v0/books/
sydwebdev139:8080/sparke/api/v0/books/<bookid>/
sydwebdev139:8080/sparke/api/v0/books/<bookid>/chronology/
sydwebdev139:8080/sparke/api/v0/books/<bookid>/chronology/bookitems/
"""

import pandas as pd
import csv
import glob
from datetime import datetime
from supporting_files.webapp_class import APIClient

# Constants
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = '00_courtbooks_to_get.csv'
OUTPUT_LOCATION = 'outputs/'

def extract_first_line(text):
    """Extracts the first line of text."""
    return text.split("\n")[0] if text else "-"

def parse_data(data):
    """Processes API response into structured rows for CSV output."""
    rows = []
    for entry in data:
        try:
            entry_date = datetime.fromtimestamp(entry.get("entryDate", 0) / 1000)
        except Exception:
            entry_date = "Invalid timestamp"

        entry_original = APIClient.clean_html(entry.get("entryOriginal", ""))
        first_line = extract_first_line(entry.get("entryFinal", ""))

        rows.append({
            "First Line": first_line,
            "Court Book ID": entry.get("courtBookId"),
            "Book Item ID": entry.get("bookItemId"),
            "Entry Date": entry_date,
            "PromptID": 1,
            "Entry_Original": entry_original,
            "Entry Description": first_line if first_line.isupper() else "-"
        })
    return rows

def save_to_csv(rows, court_book_id):
    """Saves processed data to a CSV file."""
    filename = f"{OUTPUT_LOCATION}{court_book_id}_courtbook.csv"
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"CSV file successfully saved: {filename}")

def process_court_book(client, court_book_id):
    """Fetches court book data and writes it to CSV."""
    try:
        response_data = client.fetch_api_data(f"/sparke/api/v0/books/{court_book_id}/chronology/")
        rows = parse_data(response_data)
        save_to_csv(rows, court_book_id)
        return True
    except Exception as e:
        print(f"Failed to process court book {court_book_id}: {e}")
        return False

def main():
    """Main function to process court books from the CSV file."""
    client = APIClient(BASE_URL, LOGIN_PAGE_URL, LOGIN_URL)
    if not client.authenticate():
        print("Authentication failed. Exiting.")
        return

    existing_files = set(glob.glob(f"{OUTPUT_LOCATION}*_courtbook.csv"))
    success_count = 0
    failure_count = 0

    with open(CSV_FILE, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            for court_book_id in row:
                expected_filename = f"{OUTPUT_LOCATION}{court_book_id}_courtbook.csv"
                if expected_filename not in existing_files:
                    success = process_court_book(client, court_book_id)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1
                else:
                    print(f"Skipping {court_book_id}; file exists.")

    print(f"Process completed: {success_count} court books processed successfully, {failure_count} failed.")

if __name__ == "__main__":
    main()
