import streamlit as st
import os
import requests
from PIL import Image
from dotenv import load_dotenv
from src import utils
from src.fast2sms import send_sms

# -------------------------------
# 1️⃣ Load environment variables
# -------------------------------
load_dotenv()
HF_TOKEN = os.getenv("HF_API_KEY")
if not HF_TOKEN:
    st.error("❌ Missing Hugging Face token in .env file")
    st.stop()

# -------------------------------
# 2️⃣ Emergency responses
# -------------------------------
emergencies = {
    "fire": {
        "response": "Call the fire department immediately and evacuate safely.",
        "tip": "Stay low to avoid smoke and use a fire extinguisher if safe.",
        "icon": "assets/fire.jpg"
    },
    "burglary": {
        "response": "Lock all doors, call the police, and stay safe.",
        "tip": "Do not confront intruders. Stay hidden and quiet.",
        "icon": "assets/burglary.jpg"
    },
    "medical emergency": {
        "response": "Call emergency medical services immediately. Provide first aid if trained.",
        "tip": "Check vital signs, keep patient calm and comfortable.",
        "icon": "assets/medical.png"
    },
    "kidnap": {
        "response": "Call the police immediately. Do not try to confront the kidnapper.",
        "tip": "Memorize suspect details and location.",
        "icon": "assets/kidnap.jpg"
    }
}

# -------------------------------
# 3️⃣ ML Intent Detection (HF API)
# -------------------------------
def detect_emergency_hf(text):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        candidate_labels = list(emergencies.keys())
        payload = {
            "inputs": text,
            "parameters": {"candidate_labels": candidate_labels, "multi_label": False}
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if isinstance(result, dict) and "labels" in result:
            return result["labels"][0].lower()
        else:
            return "unknown"

    except Exception as e:
        st.error(f"Error in ML model: {e}")
        return "unknown"

# -------------------------------
# 4️⃣ Streamlit UI setup
# -------------------------------
st.set_page_config(page_title="🏠 Home Emergency Assistant", layout="centered")
st.title("🏠 Multilingual Home Emergency Assistant")

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

option = st.radio("Choose input method:", ["Text", "Voice"])
user_input = ""
detected_lang = "en"

# -------------------------------
# 5️⃣ Input handling
# -------------------------------
if option == "Text":
    user_input = st.text_input("Describe your emergency:")
    if user_input:
        detected_lang = utils.translator.detect(user_input).lang
else:
    if st.button("🎤 Press to Speak"):
        user_input, detected_lang = utils.get_voice_input()
        if user_input:
            st.success(f"You said: {user_input} ({detected_lang})")
        else:
            st.error("Could not recognize your voice. Try again.")

# -------------------------------
# 6️⃣ Process input
# -------------------------------
if user_input:
    english_text = utils.translate_text(user_input, dest="en")
    emergency_type = detect_emergency_hf(english_text)

    if emergency_type in emergencies:
        response = emergencies[emergency_type]["response"]
        tip = emergencies[emergency_type]["tip"]
        icon_path = emergencies[emergency_type]["icon"]
    else:
        response = "Sorry, I am not sure how to help. Please contact emergency services."
        tip = ""
        icon_path = None

    # Translate response back to user's language
    final_response = utils.translate_text(response, dest=detected_lang)
    final_tip = utils.translate_text(tip, dest=detected_lang)

    # Store in conversation history
    st.session_state.conversation.append({
        "user": user_input,
        "emergency_type": emergency_type,
        "response": final_response,
        "tip": final_tip,
        "icon": icon_path
    })

    # Speak the response
    utils.speak(final_response, lang=detected_lang)

# -------------------------------
# 7️⃣ Display conversation history
# -------------------------------
for item in reversed(st.session_state.conversation):
    col1, col2 = st.columns([1, 3])
    if item["icon"]:
        with col1:
            st.image(item["icon"], width=80)
    with col2:
        st.subheader(f"🚨 {item['emergency_type'].capitalize()} Alert")
        st.write(item["response"])
        if item["tip"]:
            st.info(f"💡 Safety Tip: {item['tip']}")

# -------------------------------
# 8️⃣ Send emergency SMS
# -------------------------------
if st.session_state.conversation:
    if st.button("📩 Send Emergency SMS (latest)"):
        last_item = st.session_state.conversation[-1]
        message = f"{last_item['response']} {last_item['tip']}"
        success = send_sms(message)
        if success:
            st.success("📩 Emergency SMS sent successfully!")
        else:
            st.error("❌ Failed to send SMS.")
