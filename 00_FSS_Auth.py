import requests

# Create a session object to persist cookies between requests
session = requests.Session()

# Replace these with your actual login URL and credentials
login_url = "http://sydwebdev139:8080/sparke/authed/j_security_check" 
payload = {
    "j_username": "sparke.admin",
    "j_password": "dem0123"
}

# Send a POST request to the login endpoint with your credentials
login_response = session.post(login_url, data=payload, allow_redirects=True)

print(login_response)

if login_response.ok:
    print("Login successful!")
    # Automatically, the session will store the cookies.
    session_id = session.cookies.get("JSESSIONID")
    print("Session ID:", session_id)
else:
    print("Login failed!")
    # Optionally handle login failure here

