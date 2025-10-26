## SEVA AI - POWERED BY AI, YOUR MULTILINGUAL HELPER DRIVEN BY CARE
<img width="1904" height="672" alt="image" src="https://github.com/user-attachments/assets/64c3a68f-9e04-4d6f-b01f-7c2c20f1e5c5" />

SevaAI is an intelligent, voice-activated assistant designed to provide immediate, multilingual support during home emergencies. It listens to user queries in various languages, differentiates between casual chat and critical emergencies, and responds with clear, actionable advice both visually and audibly in the user's native language.

This project was built to solve a critical problem: in a crisis, language barriers should never delay a person's access to help.

---

## Core Features

* *Seamless Multilingual Support:* Users can speak or type in their native language (including English, Hindi, Kannada, Tamil, etc.). SevaAI accurately detects the language and responds in that same language.
* *Hybrid Emergency Detection:* A powerful two-step system ensures accuracy:
    1.  *Keyword Matching:* Instantly catches high-priority keywords for the fastest possible response.
    2.  *Hugging Face ML Model:* Uses a sophisticated NLP model (facebook/bart-large-mnli) to understand the context of more complex sentences.
* *Robust Casual Chat:* For non-emergency interactions, SevaAI utilizes a reliable, hardcoded chatbot, ensuring 100% uptime without the risk of external API failures.
* *High-Quality Voice Output:* All responses are spoken back to the user using edge-tts for natural-sounding, multilingual speech.
* *Dual-Layer Alert System:*
    * *Quick Alert:* A simple "Send Emergency SMS" button to instantly send a notification to a pre-configured Discord channel.
    * *Advanced Panic Button:* An escalation option that initiates a full sequence of automated voice calls (to police) and SMS messages (to emergency contacts) using Twilio.

---

## Tech Stack

* *Frontend:* Streamlit
* *Voice Input:* SpeechRecognition & PyAudio
* *Language Handling:* googletrans
* *ML Emergency Detection:* Hugging Face Inference API (requests)
* *Voice Output (TTS):* edge-tts
* *Notifications:*
    * requests (for Discord Webhooks)
    * twilio (for Voice Calls & SMS)
* *Environment Management:* python-dotenv

---

## Setup & Installation

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

git clone [https://github.com/your-username/your-repo-name.git]
cd your-repo-name
2. Create and Activate a Virtual Environment
This keeps the project's dependencies isolated.

Create:

Bash

python -m venv venv
Activate (Windows):

Bash

.\venv\Scripts\activate
Activate (Mac/Linux):

Bash

source venv/bin/activate
3. Install Dependencies
Install all required packages from the requirements.txt file.

Bash

pip install -r requirements.txt
4. Set Up Environment Variables
Create a file named .env in the project's root directory and add your secret API keys. The app will run in "simulation mode" for Twilio if these keys are left blank.

Code snippet

# Hugging Face API Key
HF_API_KEY="hf_YourHuggingFaceKeyHere"

# Discord Webhook URL for notifications
DISCORD_WEBHOOK_URL="[https://discord.com/api/webhooks/](https://discord.com/api/webhooks/)..."

# Twilio Credentials for the Panic Button
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"
TWILIO_PHONE_NUMBER="+1..." # Your Twilio phone number (e.g., from the US)

# Phone Numbers to Contact (Use E.164 format: +CountryCodeNumber)
# IMPORTANT: For trial Twilio accounts, these numbers must be verified in your Twilio dashboard.
POLICE_NUMBER="+91..." # Use a verified personal number for testing
EMERGENCY_CONTACT_1="+91..."
EMERGENCY_CONTACT_2="+91..."
5. Run the Application
Bash

streamlit run app.py
The application should now be running in your web browser!
The application should now be running in your web browser!
