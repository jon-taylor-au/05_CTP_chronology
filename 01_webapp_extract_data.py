import pandas as pd
import csv
import glob
import os
from datetime import datetime
from supporting_files.webapp_class import APIClient
from bs4 import BeautifulSoup
import uuid

# Constants
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = '00_courtbooks_to_get.csv'
OUTPUT_LOCATION = 'outputs/'

def extract_first_line(text, max_length=80):
    """Extracts the first non-empty line of text from <p> tags in an HTML string and truncates it."""
    if not text:
        return "-"

    # Parse the HTML content
    soup = BeautifulSoup(text, "html.parser")

    # Find all <p> elements
    paragraphs = soup.find_all("p")

    # Iterate through paragraphs and return the first non-empty text
    for p in paragraphs:
        clean_text = p.get_text(strip=True)  # Remove leading/trailing spaces
        if clean_text:  # Skip empty paragraphs
            return (clean_text[:max_length] + "...") if len(clean_text) > max_length else clean_text
    
    return "-"


def split_text_into_parts(text, num_parts):
    """Splits text into roughly equal parts, keeping sentence integrity if possible."""
    words = text.split()  # Tokenize by words
    split_size = len(words) // num_parts  # Words per part

    parts = []
    for i in range(num_parts):
        start = i * split_size
        end = None if i == num_parts - 1 else (i + 1) * split_size
        part_text = " ".join(words[start:end])  # Join words back into a string
        parts.append(part_text.strip())  # Remove leading/trailing spaces
    
    return parts

def parse_data(data):
    """Processes API response into structured rows for CSV output, including split text parts."""
    rows = []
    index_counter = 0  # Initialize the index counter
    TOKEN_LIMIT = 3500  # Max tokens per part

    for entry in data:
        handwritten = entry.get("handwritten", "").strip().lower()
        relevant = entry.get("relevant", "").strip()

        # Only process if Handwritten == "false" and Relevant == "Relevant"
        if handwritten != "false" or relevant != "Relevant":
            continue  # Skip this entry

        try:
            entry_date = datetime.fromtimestamp(entry.get("entryDate", 0) / 1000)
        except Exception:
            entry_date = "Invalid timestamp"

        entry_original = APIClient.clean_html(entry.get("entryOriginal", ""))
        first_line = extract_first_line(entry.get("entryFinal", ""))
        word_count = len(entry_original.split())  # Count words
        token_count = int(round(word_count * 1.3))  # Estimate token count

        # Generate a unique ID for the original entry (before splitting)
        unique_id = str(uuid.uuid4())

        # Determine the number of parts needed
        num_parts = max(1, -(-token_count // TOKEN_LIMIT))  # Equivalent to math.ceil(token_count / TOKEN_LIMIT)

        # Split `Entry_Original` into multiple parts
        entry_parts = split_text_into_parts(entry_original, num_parts)

        # Create rows for each part
        for part_index, part_text in enumerate(entry_parts, start=1):
            rows.append({
                "Index": index_counter,  # Incremental index
                "Unique ID": unique_id,  # Same ID for all parts of an entry
                "First Line": first_line,
                "Court Book ID": entry.get("courtBookId"),
                "Book Item ID": entry.get("bookItemId"),
                "Entry Date": entry_date,
                "PromptID": 1,
                "Entry_Original": part_text,  # Now only contains part of the text
                "Token Count": token_count,  # Same total token count
                "Part": f"Part {part_index}/{num_parts}",  # "Part 1/3",
                "Handwritten": handwritten,
                "Relevant": relevant,
                "Entry Description": first_line if first_line.isupper() else "-"
            })
            index_counter += 1  # Increment index for each split part

    return rows



def save_to_csv(rows, court_book_id):
    """Saves processed data to a CSV file."""
    filename = os.path.join(OUTPUT_LOCATION, f"{court_book_id}_courtbook.csv")
    df = pd.DataFrame(rows)
    # reorder the columns so Index is the first column
    cols = ["Index", "Unique ID","Part", "First Line", "Handwritten","Relevant","Court Book ID", "Book Item ID", "Entry Date", "PromptID", "Entry_Original","Token Count", "Entry Description"]
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
