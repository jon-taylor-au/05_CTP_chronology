import pandas as pd
import csv
import glob
import os
from datetime import datetime
from supporting_files.webapp_class import APIClient
from bs4 import BeautifulSoup
import uuid
import concurrent.futures

# Constants
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = '00_courtbooks_to_get.csv'
OUTPUT_LOCATION = 'outputs/'
PROGRESS_LOG = r"\\V0050\05_CTP_chronology\run_scripts\progress.log"

def log_progress(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")


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

def parse_data(data, book_item_lookup):
    """Processes API response into structured rows for CSV output, including book item descriptions."""
    rows = []
    index_counter = 0
    TOKEN_LIMIT = 3500  # Max tokens per part

    for entry in data:
        handwritten = entry.get("handwritten", "").strip().lower()
        relevant = entry.get("relevant", "").strip()
        book_item_id = str(entry.get("bookItemId"))  # Convert to string for lookup
        id = str(entry.get("id"))  # Convert to string for lookup

        # Lookup description from book items
        book_item_description = book_item_lookup.get(book_item_id, "-")  

        try:
            entry_date = datetime.fromtimestamp(entry.get("entryDate", 0) / 1000)
        except Exception:
            entry_date = "Invalid timestamp"

        entry_original = APIClient.clean_html(entry.get("entryOriginal", ""))
        entry_modified = APIClient.clean_html(entry.get("entryFinal", ""))
        first_line = extract_first_line(entry.get("entryFinal", ""))
        word_count = len(entry_original.split())  # Count words
        token_count = int(round(word_count * 1.3))  # Estimate token count

        # Generate a unique ID for the original entry
        unique_id = str(uuid.uuid4())

        if handwritten == "true":
            rows.append({
                "Index": index_counter,
                "Unique ID": unique_id,
                "First Line": first_line,
                "Court Book ID": entry.get("courtBookId"),
                "Book Item ID": book_item_id,
                "Line ID": id,
                "Book Item Description": book_item_description, 
                "Entry Date": entry_date,
                "PromptID": None,
                "Entry_Original": entry_original,
                "Entry_Modified": entry_modified,
                "Token Count": 0,
                "Part": "Part 1/1",
                "Handwritten": handwritten,
                "Relevant": relevant,
                "Entry Description": first_line if first_line.isupper() else "-",
                "Response": "** handwritten **"
            })
            index_counter += 1
            continue

        if handwritten == "false" and relevant == "Relevant":
            num_parts = max(1, -(-token_count // TOKEN_LIMIT))  # Equivalent to math.ceil(token_count / TOKEN_LIMIT)
            entry_parts = split_text_into_parts(entry_original, num_parts)

            for part_index, part_text in enumerate(entry_parts, start=1):
                rows.append({
                    "Index": index_counter,
                    "Unique ID": unique_id,
                    "First Line": first_line,
                    "Court Book ID": entry.get("courtBookId"),
                    "Book Item ID": book_item_id,
                    "Line ID": id,
                    "Book Item Description": book_item_description,  # New field
                    "Entry Date": entry_date,
                    "PromptID": 1,
                    "Entry_Original": part_text,
                    "Entry_Modified": entry_modified,
                    "Token Count": token_count,
                    "Part": f"Part {part_index}/{num_parts}",
                    "Handwritten": handwritten,
                    "Relevant": relevant,
                    "Entry Description": first_line if first_line.isupper() else "-",
                    "Response": None
                })
                index_counter += 1

    return rows

def save_to_csv(rows, court_book_id):
    """Saves processed data to a CSV file."""
    filename = os.path.join(OUTPUT_LOCATION, f"{court_book_id}_courtbook.csv")
    df = pd.DataFrame(rows)
    
    # Reorder columns to include the new field
    cols = ["Index", "Unique ID", "Part", "First Line", "Handwritten", "Relevant",
            "Court Book ID", "Book Item ID","Line ID", "Book Item Description", 
            "Entry Date", "PromptID", "Entry_Original", "Entry_Modified","Token Count", "Entry Description"]
    
    df = df[cols]
    df.to_csv(filename, index=False)
    print(f"CSV file successfully saved: {filename}")

def process_court_book(client, court_book_id):
    """Fetches court book data, retrieves book item descriptions, and writes to CSV."""
    
    # Fetch book item descriptions
    book_item_lookup = fetch_book_items(client, court_book_id)
    
    # Fetch chronology data
    response_data = client.fetch_api_data(f"/sparke/api/v0/books/{court_book_id}/chronology/")
    
    # Parse data with book item lookup
    rows = parse_data(response_data, book_item_lookup)
    
    # Save output
    save_to_csv(rows, court_book_id)

def fetch_book_items(client, court_book_id):
    """Fetch book item descriptions from the new endpoint."""
    url = f"/sparke/api/v0/books/{court_book_id}/chronology/bookitems/"
    response_data = client.fetch_api_data(url)

    # Create a lookup dictionary {id: description}
    book_item_lookup = {str(item["id"]): item["description"] for item in response_data if "id" in item and "description" in item}
    
    return book_item_lookup

def main():
    """Main function to process court books from the CSV file."""
    client = APIClient(BASE_URL, LOGIN_PAGE_URL, LOGIN_URL)
    if not client.authenticate():
        print("Authentication failed. Exiting.")
        log_progress("❌ ERROR: Authentication failed. Exiting.")
        return

    existing_files = {os.path.basename(f) for f in glob.glob(os.path.join(OUTPUT_LOCATION, "*_courtbook.csv"))}

    with open(CSV_FILE, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header

        for row in reader:
            if not row or not row[0].strip():
                continue

            court_book_id = row[0].strip()
            expected_filename = f"{court_book_id}_courtbook.csv"

            if expected_filename in existing_files:
                print(f"Skipping {court_book_id}; file exists.")
                log_progress(f"ℹ️ Skipping {court_book_id}; file already exists.")
            else:
                try:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(process_court_book, client, court_book_id)
                        future.result(timeout=30)
                except concurrent.futures.TimeoutError:
                    error_msg = f"❌ ERROR: Timed out processing court book ID {court_book_id} (over 30s)"
                    print(error_msg)
                    log_progress(error_msg)



if __name__ == "__main__":
    main()