import streamlit as st
import os
import requests
from dotenv import load_dotenv
from src import utils
from src.discord_notify import send_sms
import base64
import time

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_API_KEY")
if not HF_TOKEN:
    st.error("⚠️ Missing Hugging Face API key in .env file.")
    st.stop()

# Emergency Definitions
emergencies = {"fire": {"response": "Call the fire department immediately and evacuate safely.", "tip": "Stay low to avoid smoke and use a fire extinguisher if safe.", "icon": "assets/fire.jpg"}, "burglary": {"response": "Lock all doors, call the police, and stay safe.", "tip": "Do not confront intruders. Stay hidden and quiet.", "icon": "assets/burglary.jpg"}, "medical emergency": {"response": "Call emergency medical services immediately. Provide first aid if trained.", "tip": "Check vital signs, keep patient calm and comfortable.", "icon": "assets/medical.png"}, "kidnap": {"response": "Call the police immediately. Do not try to confront the kidnapper.", "tip": "Memorize suspect details and location.", "icon": "assets/kidnap.jpg"}, "gas leak": {"response": "Evacuate immediately and call the gas company or emergency services.", "tip": "Do not use electrical switches, matches, or lighters.", "icon": "assets/gas_leak.jpg"}, "domestic violence": {"response": "Call the police and seek safe shelter immediately.", "tip": "Avoid confrontation and keep emergency numbers handy.", "icon": "assets/domestic_violence.jpg"}, "heart attack": {"response": "Call emergency medical services immediately and perform CPR if trained.", "tip": "Keep the patient calm and seated. Loosen tight clothing.", "icon": "assets/heart_attack.jpg"}, "food poisoning": {"response": "Call medical services if severe symptoms appear. Keep hydrated.", "tip": "Do not induce vomiting. Monitor for dehydration.", "icon": "assets/food_poisoning.jpg"}, "natural disaster": {"response": "Follow local safety guidelines and evacuate if necessary.", "tip": "Keep emergency supplies and stay informed via official alerts.", "icon": "assets/natural_disaster.jpg"}}

emergency_keywords = {
    "heart attack": ["chest pain", "heart attack", "cardiac arrest", "breathing difficulty", "shortness of breath"],
    "food poisoning": ["stomach pain", "vomiting", "nausea", "diarrhea", "food poisoning", "pet dard"]
}

def check_keyword_override(text_lower):
    if any(kw in text_lower for kw in ["husband", "wife", "partner"]) and any(kw in text_lower for kw in ["beating", "hitting", "hurting", "assault", "abuse"]):
        return "domestic violence"
    for emergency, keywords in emergency_keywords.items():
        if any(kw in text_lower for kw in keywords): 
            return emergency
    return None

def render_emergency_call_popup():
    st.markdown("""
    <div class="emergency-overlay">
        <div class="emergency-call-card">
            <div class="ripple-container">
                <div class="ripple"></div>
                <div class="ripple"></div>
                <div class="ripple"></div>
                <div class="phone-icon">📞</div>
            </div>
            <h2 class="call-status-title">Connecting to Emergency Services...</h2>
            <p class="call-status-subtitle">Notifying emergency contacts via SMS...</p>
            <div class="call-progress-bar">
                <div class="call-progress-fill"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_panic_button(data):
    if st.button("Initiate Emergency Sequence", key="panic_btn", use_container_width=True):
        msg_to_send = f"🚨 EMERGENCY: {data['emergency_type'].title()}. {data['response']}"
        send_sms(msg_to_send)
        st.session_state.call_in_progress = True
        st.rerun()

def detect_emergency_hf(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    candidate_labels = list(emergencies.keys())
    payload = {"inputs": text, "parameters": {"candidate_labels": candidate_labels}}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        if result and result['scores'][0] > 0.50: 
            return result['labels'][0].lower()
    except Exception as e:
        print(f"API Error: {e}")
    return "casual conversation"

hardcoded_intents = {
    "greeting": {"keywords": ["hello", "hi", "hey", "namaste"], "responses": {"en": "Hello! How can I assist you today?"}},
    "name": {"keywords": ["your name", "who are you"], "responses": {"en": "I'm SevaAI, your multilingual emergency assistant."}},
    "thanks": {"keywords": ["thank you", "thanks"], "responses": {"en": "You're welcome!"}},
}

def get_hardcoded_response(user_input_en, lang='en'):
    user_input_en = user_input_en.lower().strip()
    for intent_data in hardcoded_intents.values():
        if any(keyword in user_input_en for keyword in intent_data["keywords"]):
            return intent_data["responses"].get(lang, intent_data["responses"]['en'])
    return "I am here to help with emergencies. Please describe the situation."

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Page Configuration
st.set_page_config(page_title="SevaAI", layout="centered", initial_sidebar_state="collapsed")

# CSS Styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #ffffff;
        min-height: 100vh;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 0;
        gap: 1.5rem;
    }
    
    .logo-img {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6);
        border: 3px solid #667eea;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .tagline {
        font-size: 1rem;
        color: #c4c4e8;
        margin: 0.5rem 0 0 0;
        font-style: italic;
    }
    
    .method-button {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 2rem 3rem;
        border-radius: 25px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        text-align: center;
        transition: all 0.4s ease;
    }
    
    .method-button.active {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        border-color: #667eea;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.6);
        transform: scale(1.05);
    }
    
    .method-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .method-label {
        color: #e0e0ff;
        font-weight: 600;
        font-size: 1.2rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .stButton>button {
        border-radius: 50px !important;
        padding: 0.85rem 2.8rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.8) !important;
    }
    
    .stChatInput > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 35px !important;
    }
    
    .stChatInput input {
        color: #ffffff !important;
        font-size: 1.05rem !important;
    }
    
    .emergency-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(10px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .emergency-call-card {
        background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
        border-radius: 30px;
        padding: 3rem 4rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 255, 136, 0.5);
        max-width: 500px;
        width: 90%;
    }
    
    .phone-icon {
        font-size: 5rem;
        margin-bottom: 1.5rem;
        display: inline-block;
        animation: phonePulse 1.5s ease-in-out infinite;
    }
    
    @keyframes phonePulse {
        0%, 100% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.1) rotate(-10deg); }
        75% { transform: scale(1.1) rotate(10deg); }
    }
    
    .call-status-title {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    .call-status-subtitle {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .call-progress-bar {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        overflow: hidden;
        margin: 2rem 0;
    }
    
    .call-progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #ffffff 0%, #f0f0f0 100%);
        animation: progressLoad 3s ease-out forwards;
    }
    
    @keyframes progressLoad {
        from { width: 0%; }
        to { width: 100%; }
    }
    
    .ripple-container {
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto 2rem;
    }
    
    .ripple {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 120px;
        height: 120px;
        border: 3px solid rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: rippleEffect 2s ease-out infinite;
    }
    
    .ripple:nth-child(2) { animation-delay: 0.5s; }
    .ripple:nth-child(3) { animation-delay: 1s; }
    
    @keyframes rippleEffect {
        0% { width: 60px; height: 60px; opacity: 1; }
        100% { width: 180px; height: 180px; opacity: 0; }
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #ffffff !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state: 
    st.session_state.messages = []
if "speak_now" not in st.session_state: 
    st.session_state.speak_now = None
if "alert_audio_played" not in st.session_state: 
    st.session_state.alert_audio_played = False
if "call_in_progress" not in st.session_state: 
    st.session_state.call_in_progress = False
if "current_page" not in st.session_state: 
    st.session_state.current_page = "home"
if "input_method" not in st.session_state: 
    st.session_state.input_method = "text"
if "casual_audio_played" not in st.session_state:
    st.session_state.casual_audio_played = False

# ✨ FIX: Create TTS placeholder (THIS IS THE CRITICAL MISSING PIECE!)
if "tts_placeholder" not in st.session_state:
    st.session_state.tts_placeholder = st.empty()

# Header
logo_path = "logo.jpeg"
logo_base64 = get_base64_image(logo_path)

if logo_base64:
    st.markdown(f"""
    <div class="header-container">
        <img src="data:image/jpeg;base64,{logo_base64}" class="logo-img">
        <div class="title-section">
            <h1 class="main-title">SevaAI</h1>
            <p class="tagline">Powered by AI, your multilingual helper driven by care</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-container">
        <div class="title-section" style="text-align: center;">
            <h1 class="main-title">SevaAI</h1>
            <p class="tagline">Powered by AI, your multilingual helper driven by care</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Page Navigation
if st.session_state.current_page == "response":
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Home", key="back_btn"):
        st.session_state.current_page = "home"
        st.session_state.casual_audio_played = False  # Reset for next interaction
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show emergency call popup
    if st.session_state.get("call_in_progress", False):
        render_emergency_call_popup()
        time.sleep(5)
        st.session_state.call_in_progress = False
        st.rerun()
    
    is_emergency_active = any(msg.get("role") == "alert" for msg in st.session_state.messages)
    
    if is_emergency_active:
        alert_item = next((msg for msg in st.session_state.messages if msg["role"] == "alert"), None)
        if alert_item:
            data = alert_item['data']
            
            # Play TTS audio for emergency alert
            utils.speak(data["response"], data["tip"], data["lang"], autoplay=not st.session_state.alert_audio_played)
            st.session_state.alert_audio_played = True
            
            if data.get("triggering_input"): 
                st.info(data["triggering_input"])
            
            col1, col2 = st.columns([1, 4])
            if data["icon"] and os.path.exists(data["icon"]):
                with col1: 
                    st.image(data["icon"], width=100)
            with col2:
                st.subheader(f"🚨 {data['emergency_type'].title()} Alert")
                st.write(data["response"])
                if data["tip"]: 
                    st.info(f"💡 Safety Tip: {data['tip']}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_sms, col_panic = st.columns(2)
            with col_sms:
                if st.button("Send Emergency SMS", key="sms_btn", use_container_width=True):
                    msg_to_send = f"EMERGENCY: {data['emergency_type'].title()}. {data['response']}"
                    if send_sms(msg_to_send):
                        st.success("📩 Alert sent!")
                    else:
                        st.error("⚠️ Failed to send alert.")
            
            with col_panic:
                render_panic_button(data)
    else:
        # ✨ NEW: Play TTS for casual conversation responses
        if not st.session_state.casual_audio_played and len(st.session_state.messages) > 0:
            assistant_msg = next((msg for msg in st.session_state.messages if msg["role"] == "assistant"), None)
            if assistant_msg and st.session_state.speak_now:
                utils.speak(
                    st.session_state.speak_now["response"], 
                    st.session_state.speak_now.get("tip", ""), 
                    st.session_state.speak_now.get("lang", "en"),
                    autoplay=True
                )
                st.session_state.casual_audio_played = True
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): 
                st.markdown(message["content"])

else:
    # Home Page
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            text_active = "active" if st.session_state.input_method == "text" else ""
            st.markdown(f"""
            <div class="method-button {text_active}">
                <span class="method-icon">💬</span>
                <span class="method-label">Text</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Text", key="text_btn", use_container_width=True):
                st.session_state.input_method = "text"
                st.rerun()
        
        with subcol2:
            voice_active = "active" if st.session_state.input_method == "voice" else ""
            st.markdown(f"""
            <div class="method-button {voice_active}">
                <span class="method-icon">🎤</span>
                <span class="method-label">Voice</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Voice", key="voice_btn", use_container_width=True):
                st.session_state.input_method = "voice"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    user_input, detected_lang = "", "en"
    
    if st.session_state.input_method == "text":
        prompt = st.chat_input("Describe your situation or ask a question...")
        if prompt:
            user_input = prompt
            detected_lang = utils.translator.detect(user_input).lang
    else:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🎤 Press to Speak", key="voice_btn_main", use_container_width=True):
                user_input, detected_lang = utils.get_voice_input()
    
    # Process input
    if user_input:
        english_text = utils.translate_text(user_input, dest="en")
        emergency_type = check_keyword_override(english_text.lower())
        if not emergency_type:
            emergency_type = detect_emergency_hf(english_text)

        if emergency_type and emergency_type != "casual conversation":
            st.session_state.messages.clear()
            details = emergencies.get(emergency_type)
            final_response = utils.translate_text(details["response"], dest=detected_lang)
            final_tip = utils.translate_text(details["tip"], dest=detected_lang)
            alert_data = {
                "role": "alert",
                "data": {
                    "emergency_type": emergency_type, 
                    "response": final_response, 
                    "tip": final_tip, 
                    "icon": details["icon"], 
                    "triggering_input": f"You said: {user_input} ({detected_lang})",
                    "lang": detected_lang,
                    "user": user_input 
                }
            }
            st.session_state.messages.append(alert_data)
            st.session_state.alert_audio_played = False
            st.session_state.current_page = "response"
            st.rerun()
        else:
            # ✨ FIX: Handle casual conversation with proper TTS
            st.session_state.messages.clear()
            st.session_state.messages.append({"role": "user", "content": user_input})
            final_ai_response = get_hardcoded_response(english_text, detected_lang)
            st.session_state.messages.append({"role": "assistant", "content": final_ai_response})
            
            # Store TTS data for playback on response page
            st.session_state.speak_now = {
                "response": final_ai_response, 
                "tip": "", 
                "lang": detected_lang
            }
            st.session_state.casual_audio_played = False  # Reset the flag
            st.session_state.current_page = "response"
            st.rerun()