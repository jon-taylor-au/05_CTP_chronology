import pandas as pd
import csv
import glob
import os
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
    """Processes API response into structured rows for CSV output, including an index."""
    rows = []
    index_counter = 0  # Initialize the index counter
    for entry in data:
        try:
            entry_date = datetime.fromtimestamp(entry.get("entryDate", 0) / 1000)
        except Exception:
            entry_date = "Invalid timestamp"

        entry_original = APIClient.clean_html(entry.get("entryOriginal", ""))
        first_line = extract_first_line(entry.get("entryFinal", ""))
        word_count = len(entry_original.split())  # Calculate word count

        rows.append({
            "Index": index_counter,  # Add the index to the row
            "First Line": first_line,
            "Court Book ID": entry.get("courtBookId"),
            "Book Item ID": entry.get("bookItemId"),
            "Entry Date": entry_date,
            "PromptID": 1,
            "Entry_Original": entry_original,
            "Token Count": int(round(word_count * 1.3)),  # Include word count
            "Entry Description": first_line if first_line.isupper() else "-"
        })
        index_counter += 1  # Increment the counter for the next row
    return rows

def save_to_csv(rows, court_book_id):
    """Saves processed data to a CSV file."""
    filename = os.path.join(OUTPUT_LOCATION, f"{court_book_id}_courtbook.csv")
    df = pd.DataFrame(rows)
    # reorder the columns so Index is the first column
    cols = ["Index", "First Line", "Court Book ID", "Book Item ID", "Entry Date", "PromptID", "Entry_Original","Token Count", "Entry Description"]
    df = df[cols]
    df.to_csv(filename, index=False)
    print(f"CSV file successfully saved: {filename}")

def process_court_book(client, court_book_id):
    """Fetches court book data and writes it to CSV."""
    response_data = client.fetch_api_data(f"/sparke/api/v0/books/{court_book_id}/chronology/")
    rows = parse_data(response_data)
    save_to_csv(rows, court_book_id)

def main():
    """Main function to process court books from the CSV file."""
    client = APIClient(BASE_URL, LOGIN_PAGE_URL, LOGIN_URL)
    if not client.authenticate():
        print("Authentication failed. Exiting.")
        return

    # Get the list of existing files
    existing_files = {os.path.basename(f) for f in glob.glob(os.path.join(OUTPUT_LOCATION, "*_courtbook.csv"))}

    with open(CSV_FILE, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            for court_book_id in row:
                court_book_id = court_book_id.strip()  # Ensure no extra spaces
                expected_filename = f"{court_book_id}_courtbook.csv"

                if expected_filename in existing_files:
                    print(f"Skipping {court_book_id}; file exists.")
                else:
                    process_court_book(client, court_book_id)

if __name__ == "__main__":
    main()
