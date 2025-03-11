import requests
from dotenv import load_dotenv
import os


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


def call_aggregated_data_api(access_token):
    """
    Calls the IndiGO API to retrieve aggregated data.

    Parameters:
        access_token (str): The access token for authentication.

    Returns:
        requests.Response: The response object containing the data.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the API request.
    """
    headers = { "Authorization": f"Bearer {access_token}" }
    params = {"UDID": "<UDID>",
              "fdate": "2022-08-22T10:00:00",
              "tdate": "2022-08-22T11:00:00",
              "f": "ne,nw,ns,nlr,nrl",  # choose desired fields
              "a": "1",                 # aggregation: 1=15min, 2=hourly, etc.
              "simplified": "1"}
    
    data_url = "https://core.api.bluecity.ai/s/ad"
    data_response = requests.get(data_url, headers=headers, params=params)

    return data_response


def main():
    access_token = load_access_token()

    if not access_token:
        access_token = get_access_token()

    data_response = call_aggregated_data_api(access_token)

    if data_response.status_code == 200:
        print("Data fetched successfully.")
        print(data_response.json())  # Or save it as a file
    else:
        print("Data fetch failed:", data_response.status_code, data_response.text)
        if data_response.status_code == 401:  # Unauthorized, token might be expired
            access_token = get_access_token()
            data_response = call_aggregated_data_api(access_token)
            if data_response.status_code == 200:
                print("Data fetched successfully.")
                print(data_response.json())  # Or save it as a file
            else:
                print("Data fetch failed:", data_response.status_code, data_response.text)


if __name__ == "__main__":
    main()