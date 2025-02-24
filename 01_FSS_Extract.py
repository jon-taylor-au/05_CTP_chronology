import requests
from datetime import datetime
from bs4 import BeautifulSoup
from html import unescape
import pandas as pd

session_id = "B7F19FDA0672BA41F5AC8B2EE0BB20B4"
court_book_id = "11616"

def clean_html(html_content):
    """
    Remove HTML tags and convert HTML entities to plain text.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return unescape(text)

# URL for the API call
url = "http://sydwebdev139:8080/sparke/api/v0/books/" + court_book_id + "/chronology/"

# Define the headers to mimic your Postman request
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-AU,en-US;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
}

# Set the cookie with the JSESSIONID value
cookies = {
    "JSESSIONID": session_id
}

# Make the GET request
response = requests.get(url, headers=headers, cookies=cookies)

# Print response headers and text for debugging
print("Response Headers:", response.headers)
#print("Response Text:", response.text)

# Attempt to parse the JSON response
try:
    data = response.json()
except Exception as e:
    print("Failed to decode JSON. The response may not be JSON as expected.")
    raise e

# Prepare a list to collect each row as a dictionary
rows = []

# Iterate over each entry and extract the desired elements
for entry in data:
    courtBookId = entry.get("courtBookId")
    bookItemId = entry.get("bookItemId")
    entry_date_ms = entry.get("entryDate")
    entry_original_html = entry.get("entryOriginal")
    
    # Convert the Unix timestamp (milliseconds) to a human-readable date.
    try:
        entry_date = datetime.fromtimestamp(entry_date_ms / 1000)
    except Exception:
        entry_date = f"Invalid timestamp: {entry_date_ms}"
    
    # Clean the HTML content
    entry_original = clean_html(entry_original_html)
    
    # Collect the row data in a dictionary
    row = {
        "Court Book ID": courtBookId,
        "Book Item ID": bookItemId,
        "Entry Date": entry_date,
        "Entry Original": entry_original
    }
    rows.append(row)

# Use the courtBookId from the first record (if available) for the file name.
if rows:
    #file_name = f"webapp_extract_{rows[0]['Court Book ID']}.csv"
    file_name = f"fss_webapp_extract.csv"
else:
    file_name = "fss_webapp_extract.csv"

# Create a DataFrame and write it to a CSV file
df = pd.DataFrame(rows)
df.to_csv(file_name, index=False)

print(f"Data successfully written to {file_name}")
