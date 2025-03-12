"""
Author: Fengze Yang <fred.yang@utah.edu>

This script demonstrates how to call the IndiGO API to retrieve aggregated data. It handles the 
retrieval of access tokens and makes the API call using the token for authentication.
"""

import requests
from test_get_access_token import get_access_token, load_access_token


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
    """
    Main function to load the access token, call the API, and handle the response.
    """
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
    