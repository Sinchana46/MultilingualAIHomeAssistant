# fast2sms.py
import os
import requests
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")  # can be comma-separated numbers

# -------------------------------
# Send SMS function
# -------------------------------
def send_sms(message: str) -> bool:
    """
    Send an emergency SMS via Fast2SMS.

    Args:
        message (str): The message content.

    Returns:
        bool: True if SMS sent successfully, False otherwise.
    """
    if not FAST2SMS_API_KEY or not EMERGENCY_CONTACT:
        print("❌ Missing API key or contact number")
        return False

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

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ SMS sent successfully!")
            return True
        else:
            print(f"❌ Failed to send SMS. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception while sending SMS: {e}")
        return False
