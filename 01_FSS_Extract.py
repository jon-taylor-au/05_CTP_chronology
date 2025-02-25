import requests
from datetime import datetime
from bs4 import BeautifulSoup
from html import unescape
import pandas as pd
from dotenv import load_dotenv
import os
import csv
import glob

# CONSTANTS
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = '00_courtbooks_to_get'  # CSV containing court book IDs

def load_credentials():
    """Load USER and PASSWORD from the .env file."""
    load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    if not user or not password:
        raise ValueError("Missing USER or PASSWORD environment variable.")
    return user, password

def authenticate(session, user, password):
    """
    Perform authentication:
      1. GET the login page to initiate a session.
      2. POST credentials to the authentication endpoint.
    Returns the authenticated session.
    """
    # Initiate session by visiting the login page.
    session.get(LOGIN_PAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
    
    payload = {
        "j_username": user,
        "j_password": password
    }
    login_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": LOGIN_PAGE_URL,
        "Origin": BASE_URL,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = session.post(
        LOGIN_URL,
        data=payload,
        headers=login_headers,
        allow_redirects=True,
        timeout=10
    )
    
    print("POST Status Code:", response.status_code)
    print("Final URL after redirects:", response.url)
    for resp in response.history:
        print("Redirected:", resp.status_code, resp.url)
    
    session_id = session.cookies.get("JSESSIONID")
    print("Session ID:", session_id)
    return session

def clean_html(html_content):
    """Remove HTML tags and convert HTML entities to plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return unescape(soup.get_text(separator=" ", strip=True))

def fetch_api_data(session, court_book_id):
    """Fetch data from the API for the given court book ID."""
    api_url = f"{BASE_URL}/sparke/api/v0/books/{court_book_id}/chronology/"
    api_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-AU,en-US;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = session.get(api_url, headers=api_headers)
    return response

def parse_data(data):
    """Parse JSON data into a list of dictionaries."""
    rows = []
    for entry in data:
        court_book_id = entry.get("courtBookId")
        book_item_id = entry.get("bookItemId")
        entry_date_ms = entry.get("entryDate")
        prompt_id = 1  # Assuming a default value for prompt ID
        entry_original_html = entry.get("entryOriginal")
        
        try:
            entry_date = datetime.fromtimestamp(entry_date_ms / 1000)
        except Exception:
            entry_date = f"Invalid timestamp: {entry_date_ms}"
        
        entry_original = clean_html(entry_original_html)
        
        rows.append({
            "Court Book ID": court_book_id,
            "Book Item ID": book_item_id,
            "Entry Date": entry_date,
            "PromptID": prompt_id,
            "Entry_Original": entry_original
        })
    return rows

def save_to_csv(rows, court_book_id):
    """Save the parsed rows to a CSV file named '{court_book_id}_courtbook.csv'."""
    filename = f"{court_book_id}_courtbook.csv"
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"Data successfully written to {filename}")

def process_court_book(court_book_id):
    """Authenticate, fetch API data for a court book ID, parse it, and save to CSV."""
    print(f"\nProcessing {court_book_id}_courtbook.csv")
    user, password = load_credentials()
    session = requests.Session()
    authenticate(session, user, password)
    
    response = fetch_api_data(session, court_book_id)
    try:
        data = response.json()
    except Exception as e:
        print(f"Failed to decode JSON for court book ID {court_book_id}.")
        raise e
    
    rows = parse_data(data)
    save_to_csv(rows, court_book_id)

def main():
    # Get set of existing files matching the pattern.
    existing_files = set(glob.glob("*_courtbook.csv"))
    
    # Open the CSV file containing court book IDs.
    with open(CSV_FILE, newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        
        for row in reader:
            for court_book_id in row:
                expected_filename = f"{court_book_id}_courtbook.csv"
                if expected_filename not in existing_files:
                    process_court_book(court_book_id)
                else:
                    print(f"Skipping {expected_filename}; file exists.")

if __name__ == "__main__":
    main()
