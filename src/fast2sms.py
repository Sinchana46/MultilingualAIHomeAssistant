import requests
import os

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")

def send_sms(message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        'authorization': FAST2SMS_API_KEY,
        'Content-Type': "application/json"
    }
    payload = {
        "route": "v3",
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "numbers": EMERGENCY_CONTACT
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200
