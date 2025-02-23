import json
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings from urllib3
warnings.simplefilter('ignore', InsecureRequestWarning)

# Constants
BASE_URL = 'https://sparkechat.sparke.com.au'
SECRETS_FILE = "G:/01_Python/secrets.json"
RETRY_INTERVAL = 5  # Time in seconds to wait before checking task status

class LLMClient:
    def __init__(self, secrets_file="G:/01_Python/secrets.json"):
        """Initialize the LLMClient by loading credentials and retrieving the token."""
        with open(SECRETS_FILE, 'r') as file:
            secrets = json.load(file)
        self.username    = secrets['username']
        self.email       = secrets['email']
        self.password    = secrets['password']
        self.token_async = self.get_access_token(sync=False)
        self.token_sync  = self.get_access_token(sync=True)

    def get_access_token(self, sync=False):
        """Retrieve the access token from the API."""
        endpoint = "/api/v1/shared/access-token"
        params = {
            "tenantID": "sparke",
            "productID": "chat",
            "expiry": "100000",
            "endUserID": self.email,  # Use stored username from secrets file
            "scopes": "summary:sync" if sync else "summary:async"
        }

        response = requests.get(f"{BASE_URL}{endpoint}", params=params, auth=(self.username, self.password), verify=False)

        if response.status_code == 200:
            return response.json().get("accessToken")
        else:
            print(f"Failed to get token: {response.status_code} - {response.text}")
            return None

    def add_document(self, file_name):
        """Add a document and return the upload URL and document ID."""
        endpoint = '/api/v1/chat-summary/documents/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token_async}'
        }
        data = {"fileName": file_name}
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, verify=False)

        if response.status_code in [200, 201]:
            result = response.json()
            return result.get('uploadURL'), result.get('id')
        else:
            print(f"Failed to add document: {response.status_code} - {response.text}")
            return None, None

    def upload_document(self, upload_url, file_path):
        """Upload the document to the provided upload URL."""
        with open(file_path, "rb") as file:
            response = requests.put(upload_url, headers={'Content-Type': 'application/pdf'}, data=file, verify=False)
            
            if response.status_code == 200:
                print(f"File '{file_path}' uploaded successfully!")
            else:
                print(f"File upload failed with status code {response.status_code} - {response.text}")

    def add_task(self, doc_id, prompt):
        """Create a processing task for the uploaded document."""
        endpoint = '/api/v1/chat-summary/tasks/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token_async}'
        }
        data = {"docID": doc_id, "prompt": prompt, "meta_prompt": ""}
        response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, verify=False)

        if response.status_code in [200, 201]:
            return response.json().get('id')
        else:
            print(f"Failed to create task: {response.status_code} - {response.text}")
            return None

    def check_task_status(self, task_id, file_name):
        """Check task status asynchronously."""
        endpoint = f'/api/v1/chat-summary/tasks/{task_id}/status'
        headers = {'Authorization': f'Bearer {self.token_async}'}

        while True:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, verify=False)

            if response.status_code == 200:
                status = response.json().get('status')
                print(f"Current task status: {status} ({file_name})")  
                if status == "done":
                    return True
            else:
                print(f"Failed to check task status for {file_name}: {response.status_code} - {response.text}")
                return False


    def get_results(self, task_id):
        """Retrieve the processed task results."""
        endpoint = f'/api/v1/chat-summary/tasks-results?taskIDs={task_id}'
        headers = {'Authorization': f'Bearer {self.token_async}'}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve results: {response.status_code} - {response.text}")
            return None

    def send_chat_request(self, text, prompt):
        """Send a chat request to the LLM endpoint and return only the extracted 'content'."""
        url = "https://sparkechat.sparke.com.au/api/v1/chat-summary/chat/"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Authorization': f'Bearer {self.token_sync}'
        }
        payload = json.dumps({
            "text": text,
            "prompt": prompt
        })

        response = requests.post(url, headers=headers, data=payload, verify=False, stream=True)

        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        extracted_content = ""  # Store extracted content

        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8").replace("data: ", "")  # Remove 'data:' prefix
                    try:
                        json_data = json.loads(line)
                        if "content" in json_data:  # Only extract 'content' fields
                            extracted_content += json_data["content"]
                    except json.JSONDecodeError:
                        continue  # Ignore lines that aren't valid JSON
        except requests.RequestException as e:
            return f"Error processing response: {e}"

        return extracted_content.strip() if extracted_content else "Error: No content extracted"


