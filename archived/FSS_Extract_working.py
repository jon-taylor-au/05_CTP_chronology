import requests
from datetime import datetime

# URL for the API call
url = "http://sydwebdev139:8080/sparke/api/v0/books/11616/chronology/"

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
    "JSESSIONID": "65AA3D14B39783AACBE84F1ADE1E10B4"
}

# Make the GET request
response = requests.get(url, headers=headers, cookies=cookies)

# Parse the JSON response using response.json()
data = response.json()

# Iterate over each entry and extract the desired elements
for entry in data:
    entry_id = entry.get("id")
    entry_date_ms = entry.get("entryDate")
    entry_original = entry.get("entryOriginal")
    entry_final = entry.get("entryFinal")
    
    # Optionally, convert the Unix timestamp (in milliseconds) to a human-readable date.
    try:
        entry_date = datetime.fromtimestamp(entry_date_ms / 1000)
    except Exception as e:
        entry_date = f"Invalid timestamp: {entry_date_ms}"
    
    print("ID:", entry_id)
    print("Entry Date (raw):", entry_date_ms)
    print("Entry Date (formatted):", entry_date)
    print("Entry Original:", entry_original)
    print("Entry Final:", entry_final)
    print("-" * 40)
