import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from html import unescape

class APIClient:
    """Reusable API client for handling authentication and API requests."""
    
    def __init__(self, base_url, login_page, login_url):
        self.base_url = base_url
        self.login_page = login_page
        self.login_url = login_url
        self.session = requests.Session()
        self.user, self.password = self.load_credentials()

    def load_credentials(self):
        """Load credentials from .env file."""
        load_dotenv()
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
        if not user or not password:
            raise ValueError("Missing USER or PASSWORD environment variable.")
        return user, password

    def authenticate(self):
        """Authenticate and maintain session."""
        self.session.get(self.login_page, headers={"User-Agent": "Mozilla/5.0"})
        payload = {"j_username": self.user, "j_password": self.password}
        login_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": self.login_page,
            "Origin": self.base_url,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = self.session.post(self.login_url, data=payload, headers=login_headers, allow_redirects=True, timeout=10)
        return response.status_code == 200

    def fetch_api_data(self, endpoint):
        """Fetch data from the specified API endpoint with better error handling."""
        url = f"{self.base_url}{endpoint}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            
            # Print raw response for debugging
            print(f"API Response (Status {response.status_code})")  

            # Handle non-200 responses
            if response.status_code != 200:
                print(f"API request failed: {response.status_code} - {response.text}")
                return None

            # Handle empty response
            if not response.text.strip():
                print("Warning: API response is empty.")
                return None
            
            return response.json()  # Attempt to parse JSON
        
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None
        except requests.exceptions.JSONDecodeError:
            print(f"JSON decode error: Response is not valid JSON. Raw response: {response.text}")
            return None

    def send_put_request(self, endpoint, data):
        """Sends a PUT request with JSON data to the specified API endpoint."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
        try:
            response = self.session.put(url, json=data, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                print(f"PUT request successful: {response.status_code}")
            else:
                print(f"PUT request failed: {response.status_code} - {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error sending PUT request: {e}")
            return None

    @staticmethod
    def clean_html(html_content):
        """Convert HTML to clean text and ensure a non-empty result."""
        if not html_content:  # If input is None or empty
            return ""  

        soup = BeautifulSoup(html_content, "html.parser")
        text = unescape(soup.get_text(separator=" ", strip=True))
        
        return text if text else ""  # Ensure we never return None