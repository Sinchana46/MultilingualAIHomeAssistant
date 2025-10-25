# src/discord_notify.py
import os
import requests
from dotenv import load_dotenv
import asyncio # Added for async function

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_sms(message: str) -> bool:
    """Sends a simple message to Discord (original function)."""
    if not DISCORD_WEBHOOK_URL:
        print("❌ Missing DISCORD_WEBHOOK_URL in .env")
        return False
    try:
        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Exception sending Discord message: {e}")
        return False

# ✨ NEW FEATURE: Added this function required by panic_button.py
async def send_discord_alert(message: str):
    """Sends a formatted emergency alert embed to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not configured.")
        return False
    try:
        # This payload creates a nicely formatted embed message
        payload = {
            "embeds": [{
                "title": "🚨 EMERGENCY ALERT 🚨",
                "description": message,
                "color": 15158332,  # Red color
                "footer": {"text": "Alert sent via Home Emergency Assistant"}
            }]
        }
        # Use requests for async compatibility in this context
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10))
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")
        return False