import requests
import os
from dotenv import load_dotenv

# Global & constant parameters
TOKEN_FILE = "access_token.txt"

# Load .env file
load_dotenv()

# Read credentials
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

def get_access_token():
    """
    Retrieves an access token by making a POST request to the token URL with the provided credentials.

    Returns:
        str: The access token if the request is successful.
    Raises:
        SystemExit: If the token request fails.
    """
    token_url = "https://core.api.bluecity.ai/api/token/"

    credentials = {
        "username": username,
        "password": password
    }
    token_response = requests.post(token_url, json=credentials)

    if token_response.status_code == 200:
        tokens = token_response.json()
        access_token = tokens["access"]

        save_access_token(access_token)

        print("Access token acquired successfully.")
        return access_token
    else:
        print("Token request failed:", token_response.status_code, token_response.text)
        exit()

def save_access_token(token):
    """
    Saves the access token to a file.

    Parameters:
        - token (str): The access token to be saved.

    Returns:
        None
    """
    with open(TOKEN_FILE, "w") as file:
        file.write(token)

def load_access_token():
    """
    Load the access token from the specified file.

    Returns:
        str: The access token if it exists in the file, otherwise None.
    """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
        
    return None
