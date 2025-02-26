import requests
from datetime import datetime
from bs4 import BeautifulSoup
from html import unescape
import pandas as pd
from dotenv import load_dotenv
import os
import csv
import glob
import re

# CONSTANTS
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
CSV_FILE = '00_courtbooks_to_get.csv'  # CSV containing court book IDs
OUTPUT_LOCATION = 'outputs/'  # Folder to save the output files

def load_credentials():
    load_dotenv()
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    if not user or not password:
        raise ValueError("Missing USER or PASSWORD environment variable.")
    return user, password

def authenticate(session, user, password):
    session.get(LOGIN_PAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
    payload = {"j_username": user, "j_password": password}
    login_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": LOGIN_PAGE_URL,
        "Origin": BASE_URL,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = session.post(LOGIN_URL, data=payload, headers=login_headers, allow_redirects=True, timeout=10)
    session_id = session.cookies.get("JSESSIONID")
    return session

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return unescape(soup.get_text(separator=" ", strip=True))

def filter_entry_description(entry_final):
    lines = entry_final.split("\n")
    if lines and lines[0].isupper():
        return lines[0]
    return "-"

def fetch_api_data(session, court_book_id):
    api_url = f"{BASE_URL}/sparke/api/v0/books/{court_book_id}/chronology/"
    api_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}
    response = session.get(api_url, headers=api_headers)
    return response

def extract_first_line(text):
    """Extracts the first line of the text."""
    return text.split("\n")[0] if text else "-"

def parse_data(data):
    rows = []
    for entry in data:
        court_book_id = entry.get("courtBookId")
        book_item_id = entry.get("bookItemId")
        entry_date_ms = entry.get("entryDate")
        prompt_id = 1  
        entry_original_html = entry.get("entryOriginal")
        entry_final_html = entry.get("entryFinal")
        
        try:
            entry_date = datetime.fromtimestamp(entry_date_ms / 1000)
        except Exception:
            entry_date = f"Invalid timestamp: {entry_date_ms}"
        
        entry_original = clean_html(entry_original_html)
        first_line = extract_first_line(entry_final_html)
        
        rows.append({
            "First Line": first_line,
            "Court Book ID": court_book_id,
            "Book Item ID": book_item_id,
            "Entry Date": entry_date,
            "PromptID": prompt_id,
            "Entry_Original": entry_original,
            "Entry Description": clean_html(first_line)
        })
    return rows

def clean_entry_description(df):
    """Remove values in 'Entry Description' that contain lowercase characters."""
    df['Entry Description'] = df['Entry Description'].apply(lambda x: x if x.isupper() else '-')
    return df

def save_to_csv(rows, court_book_id):
    filename = f"{OUTPUT_LOCATION}{court_book_id}_courtbook.csv"
    df = pd.DataFrame(rows)
    df = clean_entry_description(df)
    df.to_csv(filename, index=False)

def process_court_book(court_book_id):
    user, password = load_credentials()
    session = requests.Session()
    authenticate(session, user, password)
    response = fetch_api_data(session, court_book_id)
    try:
        data = response.json()
    except Exception as e:
        raise e
    rows = parse_data(data)
    save_to_csv(rows, court_book_id)

def main():
    existing_files = set(glob.glob("*_courtbook.csv"))
    with open(CSV_FILE, newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            for court_book_id in row:
                expected_filename = f"{court_book_id}_courtbook.csv"
                if expected_filename not in existing_files:
                    process_court_book(court_book_id)
                else:
                    print(f"Skipping {expected_filename}; file exists.")

if __name__ == "__main__":
    main()
