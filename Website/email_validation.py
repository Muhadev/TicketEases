import requests
from requests.structures import CaseInsensitiveDict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def is_valid(email: str):
    url = f"https://api.emailvalidation.io/v1/info?email={email}"

    headers = CaseInsensitiveDict()
    # Access API key from environment variable
    headers["apikey"] = os.getenv("API_KEY")

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_resp = response.json()
        format_valid = json_resp["format_valid"]
        mx_found = json_resp["mx_found"]
        smtp_check = json_resp["smtp_check"]
        state = json_resp["state"]

        return format_valid and mx_found and smtp_check and state == "deliverable"

    return False
