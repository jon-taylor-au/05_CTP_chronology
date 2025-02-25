import requests
from datetime import datetime
from bs4 import BeautifulSoup
from html import unescape
import pandas as pd
from dotenv import load_dotenv
import os

# CONSTANTS
COURT_BOOK_ID = "11616"
BASE_URL = "http://sydwebdev139:8080"
LOGIN_PAGE_URL = f"{BASE_URL}/sparke/authed/user.action?cmd=welcome"
LOGIN_URL = f"{BASE_URL}/sparke/authed/j_security_check"
API_URL = f"{BASE_URL}/sparke/api/v0/books/{COURT_BOOK_ID}/chronology/"

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

    # Prepare login payload and headers.
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

    # Send login POST request.
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

def fetch_api_data(session):
    """Fetch data from the API using the authenticated session."""
    api_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-AU,en-US;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = session.get(API_URL, headers=api_headers)
    #print("Response Headers:", response.headers)
    return response

def parse_data(data):
    """Parse JSON data into a list of dictionaries."""
    rows = []
    for entry in data:
        court_book_id = entry.get("courtBookId")
        book_item_id = entry.get("bookItemId")
        entry_date_ms = entry.get("entryDate")
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
            "Entry Original": entry_original
        })
    return rows

def save_to_csv(rows, filename=f"{COURT_BOOK_ID}_courtbook.csv"):
    """Save the parsed rows to a CSV file."""
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"Data successfully written to {filename}")

def main():
    user, password = load_credentials()
    session = requests.Session()
    
    # Authenticate and obtain a valid session.
    authenticate(session, user, password)
    
    # Fetch API data using the authenticated session.
    response = fetch_api_data(session)
    
    try:
        data = response.json()
    except Exception as e:
        print("Failed to decode JSON. The response may not be JSON as expected.")
        raise e

    rows = parse_data(data)
    save_to_csv(rows)

if __name__ == "__main__":
    main()
