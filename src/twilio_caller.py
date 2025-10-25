import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Emergency contacts
EMERGENCY_CONTACTS = {
    "contact1": os.getenv("EMERGENCY_CONTACT_1"),
    "contact2": os.getenv("EMERGENCY_CONTACT_2"),
    "police": os.getenv("POLICE_NUMBER")
}

# Check if Twilio is configured
TWILIO_CONFIGURED = all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER])

if TWILIO_CONFIGURED:
    try:
        from twilio.rest import Client
    except ImportError:
        print("Twilio library not installed. Run: pip install twilio")
        TWILIO_CONFIGURED = False


def make_emergency_call(to_number, emergency_type, location):
    """
    Make an actual phone call using Twilio

    Args:
        to_number: Phone number to call (E.164 format: +919876543210)
        emergency_type: Type of emergency
        location: Location of emergency

    Returns:
        call_sid: Twilio call SID if successful, None if failed
    """
    if not TWILIO_CONFIGURED:
        print("Twilio not configured. Add credentials to .env file.")
        return None

    if not to_number:
        print("No phone number provided")
        return None

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # TwiML message
        twiml_url = "http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%20voice%3D%22alice%22%3EEmergency%20alert!%20This%20is%20an%20automated%20emergency%20call.%20A%20" + emergency_type.replace(
            " ", "%20") + "%20has%20been%20reported.%20Please%20respond%20immediately.%3C%2FSay%3E%3C%2FResponse%3E"

        call = client.calls.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method='GET'
        )

        print(f"Call initiated: {call.sid}")
        return call.sid

    except Exception as e:
        print(f"Error making call: {e}")
        return None


def send_emergency_sms(to_number, emergency_type, location, message_details):
    """
    Send SMS instead of calling (more reliable for demos)

    Args:
        to_number: Phone number to SMS
        emergency_type: Type of emergency
        location: Location
        message_details: Additional details
    """
    if not TWILIO_CONFIGURED:
        print("Twilio not configured. Add credentials to .env file.")
        return None

    if not to_number:
        print("No phone number provided")
        return None

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        sms_body = f"""🚨 EMERGENCY ALERT 🚨

Type: {emergency_type.upper()}
Location: {location}
Time: {message_details.get('timestamp', 'N/A')}

Details: {message_details.get('user_message', 'Emergency reported')}

This is an automated emergency notification.
"""

        message = client.messages.create(
            body=sms_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )

        print(f"SMS sent: {message.sid}")
        return message.sid

    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None


def call_all_emergency_contacts(emergency_type, location, user_message):
    """
    Call/SMS all emergency contacts

    Returns:
        dict with results for each contact
    """
    results = {}

    if not TWILIO_CONFIGURED:
        print("⚠️  Twilio not configured - running in simulation mode")
        # Return simulated results
        for contact_name, phone_number in EMERGENCY_CONTACTS.items():
            if phone_number:
                results[contact_name] = {
                    'phone': phone_number,
                    'status': 'simulated',
                    'sid': 'SIMULATED_' + contact_name.upper()
                }
        return results

    for contact_name, phone_number in EMERGENCY_CONTACTS.items():
        if phone_number:
            message_details = {
                'timestamp': location,
                'user_message': user_message
            }

            sid = send_emergency_sms(phone_number, emergency_type, location, message_details)

            results[contact_name] = {
                'phone': phone_number,
                'status': 'sent' if sid else 'failed',
                'sid': sid if sid else 'FAILED'
            }
        else:
            results[contact_name] = {
                'phone': 'Not configured',
                'status': 'not_configured',
                'sid': None
            }

    return results


def make_voice_call_to_police(emergency_type, location):
    """
    Make actual voice call to police (dummy number)
    """
    if not TWILIO_CONFIGURED:
        print("⚠️  Twilio not configured - simulating police call")
        return {
            'status': 'simulated',
            'call_sid': 'SIMULATED_POLICE_CALL',
            'to': EMERGENCY_CONTACTS.get("police", "Not configured"),
            'from': TWILIO_PHONE_NUMBER if TWILIO_PHONE_NUMBER else "Not configured"
        }

    police_number = EMERGENCY_CONTACTS.get("police")

    if not police_number:
        print("Police number not configured")
        return {
            'status': 'not_configured',
            'call_sid': None,
            'to': 'Not configured',
            'from': TWILIO_PHONE_NUMBER
        }

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        twiml_url = "http://twimlets.com/echo?Twiml=%3CResponse%3E%3CSay%20voice%3D%22alice%22%3EEmergency%20alert!%20This%20is%20an%20automated%20emergency%20call%20from%20the%20Home%20Emergency%20Assistant.%20A%20" + emergency_type.replace(
            " ", "%20") + "%20has%20been%20reported.%20Please%20respond%20immediately.%3C%2FSay%3E%3C%2FResponse%3E"

        call = client.calls.create(
            to=police_number,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url,
            method='GET'
        )

        print(f"Police call initiated: {call.sid}")

        return {
            'status': 'calling',
            'call_sid': call.sid,
            'to': police_number,
            'from': TWILIO_PHONE_NUMBER
        }

    except Exception as e:
        print(f"Error calling police: {e}")
        return {
            'status': 'failed',
            'call_sid': None,
            'to': police_number,
            'from': TWILIO_PHONE_NUMBER,
            'error': str(e)
        }


def get_twilio_status():
    """Check if Twilio is properly configured"""
    return {
        'configured': TWILIO_CONFIGURED,
        'account_sid': TWILIO_ACCOUNT_SID[:10] + "..." if TWILIO_ACCOUNT_SID else "Not set",
        'phone_number': TWILIO_PHONE_NUMBER if TWILIO_PHONE_NUMBER else "Not set",
        'emergency_contacts': {k: v if v else "Not set" for k, v in EMERGENCY_CONTACTS.items()}
    }