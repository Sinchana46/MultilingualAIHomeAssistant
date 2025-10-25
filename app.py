import streamlit as st
import os
import requests
from dotenv import load_dotenv
from src import utils
# ✨ FIX: Import both your simple SMS function and the panic button
from src.discord_notify import send_sms
from src.panic_button import render_panic_button

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
HF_TOKEN = os.getenv("HF_API_KEY")
if not HF_TOKEN:
    st.error("❌ Missing Hugging Face API key in .env file.")
    st.stop()

# -------------------------------
# Emergency Definitions & Keywords (No changes)
# -------------------------------
emergencies = {"fire": {"response": "Call the fire department immediately and evacuate safely.", "tip": "Stay low to avoid smoke and use a fire extinguisher if safe.", "icon": "assets/fire.jpg"}, "burglary": {"response": "Lock all doors, call the police, and stay safe.", "tip": "Do not confront intruders. Stay hidden and quiet.", "icon": "assets/burglary.jpg"}, "medical emergency": {"response": "Call emergency medical services immediately. Provide first aid if trained.", "tip": "Check vital signs, keep patient calm and comfortable.", "icon": "assets/medical.png"}, "kidnap": {"response": "Call the police immediately. Do not try to confront the kidnapper.", "tip": "Memorize suspect details and location.", "icon": "assets/kidnap.jpg"}, "gas leak": {"response": "Evacuate immediately and call the gas company or emergency services.", "tip": "Do not use electrical switches, matches, or lighters.", "icon": "assets/gas_leak.jpg"}, "domestic violence": {"response": "Call the police and seek safe shelter immediately.", "tip": "Avoid confrontation and keep emergency numbers handy.", "icon": "assets/domestic_violence.jpg"}, "heart attack": {"response": "Call emergency medical services immediately and perform CPR if trained.", "tip": "Keep the patient calm and seated. Loosen tight clothing.", "icon": "assets/heart_attack.jpg"}, "food poisoning": {"response": "Call medical services if severe symptoms appear. Keep hydrated.", "tip": "Do not induce vomiting. Monitor for dehydration.", "icon": "assets/food_poisoning.jpg"}, "natural disaster": {"response": "Follow local safety guidelines and evacuate if necessary.", "tip": "Keep emergency supplies and stay informed via official alerts.", "icon": "assets/natural_disaster.jpg"}}
emergency_keywords = {
    "heart attack": [
        # English
        "chest pain", "heart attack", "cardiac arrest", "breathing difficulty", "shortness of breath",
        # Hindi
        "seene mein dard", "dil ka daura", "saans lene mein dikkat", "seene ka dard",
        # Kannada
        "hrudaya noovu", "mukha nillu", "usiru kastavide", "hrudaya daura",
        # Tamil
        "idhaya vali", "idhaya thadumaaru", "moochu kashtam", "nanjai vali",
        # Telugu
        "hrudaya noppi", "manasika vedana", "gunde noppi", "hruyada dhadak",
        # Malayalam
        "hridaya vedana", "mizhavu vedana", "hridaya rogam", "hridaya pidippu"
    ],
    "food poisoning": [
        # English
        "stomach pain", "vomiting", "nausea", "diarrhea", "food poisoning", "loose motion", "stomach upset", "stomach", "abdominal pain",
        # Hindi
        "pet dard", "pet Dard", "Pet Dard", "pet Mein dard", "pet Mein Dard", "ulti", "matli", "dast", "khana kharab", "pet kharab", "pet mein dard", "pet", "pet Mein dard",
        # Kannada
        "jathara noovu", "ulti bartha ide", "oota nalli problem", "stomach alli vedane", "malada samasya", "hotte",
        # Tamil
        "vayiru vali", "vayiru kashtam", "vayiru thondaravu", "vayiru thunbam", "vayiru nallilla",
        # Telugu
        "vayunoppi", "vanta vasthundi", "aakali leka", "vayuvula", "aahara visam",
        # Malayalam
        "vayaru vedana", "vamanam", "ulthi", "aharam visham", "vayaru prashnam", "vayaru pidippu"
    ]
}


def check_keyword_override(text_lower):
    if any(kw in text_lower for kw in ["husband", "wife", "partner"]) and any(kw in text_lower for kw in ["beating", "hitting", "hurting", "assault", "abuse", "punching"]):
        return "domestic violence"
    for emergency, keywords in emergency_keywords.items():
        if any(kw in text_lower for kw in keywords): return emergency
    return None

# -------------------------------
# Hugging Face & Hardcoded Chatbot (No changes)
# -------------------------------
def detect_emergency_hf(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    candidate_labels = [key for key in emergencies.keys()]
    payload = {"inputs": text, "parameters": {"candidate_labels": candidate_labels}}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        if result and result['scores'][0] > 0.50: return result['labels'][0].lower()
    except Exception as e:
        print(f"Hugging Face API Error: {e}")
    return "casual conversation"

hardcoded_intents = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "greetings", "namaste", "vanakkam"],
        "responses": {"en": "Hello! How can I assist you today?", "hi": "नमस्ते! मैं आपकी कैसे सहायता कर सकता हूँ?", "kn": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?", "ta": "வணக்கம்! நான் உங்களுக்கு எப்படி உதவ முடியும்?", "te": "నమస్కారం! నేను మీకు ఎలా సహాయపడగలను?", "ml": "നമസ്കാരം! ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കും?"}
    },
    "how_are_you": {
        "keywords": ["how are you", "how's it going", "how are you doing", "kaise ho"],
        "responses": {"en": "I am just a program, but I'm operating perfectly! How can I help?", "hi": "मैं सिर्फ एक प्रोग्राम हूँ, लेकिन मैं पूरी तरह से काम कर रहा हूँ! मैं कैसे मदद कर सकता हूँ?", "kn": "ನಾನು ಕೇವಲ ಒಂದು ಪ್ರೋಗ್ರಾಂ, ಆದರೆ ನಾನು ಸಂಪೂರ್ಣವಾಗಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತಿದ್ದೇನೆ! ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?", "ta": "நான் ஒரு நிரல் மட்டுமே, ஆனால் நான் சரியாக செயல்படுகிறேன்! நான் எப்படி உதவ முடியும்?", "te": "నేను కేవలం ఒక ప్రోగ్రామ్, కానీ నేను సంపూర్ణంగా పనిచేస్తున్నాను! నేను ఎలా సహాయపడగలను?", "ml": "ഞാൻ ഒരു പ്രോഗ്രാം മാത്രമാണ്, പക്ഷേ ഞാൻ പൂർണ്ണമായി പ്രവർത്തിക്കുന്നു! ഞാൻ എങ്ങനെ സഹായിക്കും?"}
    },
    "doing": {
        "keywords": ["what are you doing", "what's up", "kar rahe ho"],
        "responses": {
            "en": "I'm here, ready to assist with any emergencies you might have.",
            "hi": "मैं यहाँ हूँ, आपकी किसी भी आपात स्थिति में सहायता के लिए तैयार हूँ।",
            "kn": "ನಾನು ಇಲ್ಲಿದ್ದೇನೆ, ನಿಮಗೆ ಯಾವುದೇ ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧನಾಗಿದ್ದೇನೆ।",
            "ta": "நான் இங்கே இருக்கிறேன், உங்களுக்கு ஏதேனும் அவசரநிலைகள் இருந்தால் உதவ தயாராக உள்ளேன்।",
            "te": "నేను ఇక్కడ ఉన్నాను, మీకు ఏవైనా అత్యవసర పరిస్థితులలో సహాయం చేయడానికి సిద్ధంగా ఉన్నాను।",
            "ml": "ഞാൻ ഇവിടെയുണ്ട്, നിങ്ങൾക്ക് എന്തെങ്കിലും അടിയന്തര സാഹചര്യങ്ങളുണ്ടെങ്കിൽ സഹായിക്കാൻ തയ്യാറാണ്."
        }
    },
    "joke": {
        "keywords": ["tell me a joke", "joke", "chutkula"],
        "responses": {
            "en": "Why don't scientists trust atoms? Because they make up everything!",
            "hi": "वैज्ञानिक परमाणुओं पर भरोसा क्यों नहीं करते? क्योंकि वे सब कुछ बनाते हैं!",
            "kn": "ವಿಜ್ಞಾನಿಗಳು ಪರಮಾಣುಗಳನ್ನು ಏಕೆ ನಂಬುವುದಿಲ್ಲ? ಏಕೆಂದರೆ ಅವು ಎಲ್ಲವನ್ನೂ ರೂಪಿಸುತ್ತವೆ!",
            "ta": "விஞ்ஞானிகள் அணுக்களை ஏன் நம்புவதில்லை? ஏனென்றால் அவை எல்லாவற்றையும் உருவாக்குகின்றன!",
            "te": "శాస్త్రవేత్తలు అణువులను ఎందుకు నమ్మరు? ఎందుకంటే అవి ప్రతిదీ తయారు చేస్తాయి!",
            "ml": "ശാസ്ത്രജ്ഞർ ആറ്റങ്ങളെ വിശ്വസിക്കാത്തത് എന്തുകൊണ്ട്? കാരണം അവ എല്ലാം ഉണ്ടാക്കുന്നു!"
        }
    },
    "creator": {
        "keywords": ["who made you", "who created you", "creator", "kisne banaya"],
        "responses": {
            "en": "I was created by a very talented programmer.",
            "hi": "मुझे एक बहुत ही प्रतिभाशाली प्रोग्रामर ने बनाया है।",
            "kn": "ನನ್ನನ್ನು ಒಬ್ಬ ಅತೀ ಪ್ರತಿಭಾವಂತ ಪ್ರೋಗ್ರಾಮರ್ ರಚಿಸಿದ್ದಾರೆ।",
            "ta": "என்னை ஒரு மிகவும் திறமையான புரோகிராமர் உருவாக்கினார்।",
            "te": "నన్ను చాలా ప్రతిభావంతులైన ప్రోగ్రామర్ సృష్టించారు।",
            "ml": "എന്നെ വളരെ കഴിവുള്ള ഒരു പ്രോഗ്രാമർ ആണ് സൃഷ്ടിച്ചത്."
        }
    },
    "age": {
        "keywords": ["how old are you", "your age", "umr kya hai"],
        "responses": {
            "en": "I don't have an age in the human sense. I am a computer program!",
            "hi": "मेरी इंसानों की तरह कोई उम्र नहीं है। मैं एक कंप्यूटर प्रोग्राम हूँ!",
            "kn": "ನನಗೆ ಮಾನವರಂತೆ ವಯಸ್ಸಿಲ್ಲ. ನಾನು ಕಂಪ್ಯೂಟರ್ ಪ್ರೋಗ್ರಾಂ!",
            "ta": "எனக்கு மனிதர்களைப் போல வயது இல்லை. நான் ஒரு கணினி நிரல்!",
            "te": "నాకు మానవ పరంగా వయస్సు లేదు. నేను కంప్యూటర్ ప్రోగ్రామ్!",
            "ml": "എനിക്ക് മനുഷ്യരെപ്പോലെ പ്രായമില്ല. ഞാൻ ഒരു കമ്പ്യൂട്ടർ പ്രോഗ്രാമാണ്!"
        }
    },
    "thanks": {
        "keywords": ["thank you", "thanks", "dhanyavaad", "shukriya", "nandri"],
        "responses": {"en": "You're welcome!", "hi": "आपका स्वागत है!", "kn": "ನಿಮಗೆ ಸ್ವಾಗತ!", "ta": "நல்வரவு!", "te": "మీకు స్వాగతం!", "ml": "സ്വാഗതം!"}
    },
    "name": {
        "keywords": ["your name", "who are you", "naam kya hai"],
        "responses": {"en": "You can call me Jarvis. I'm your home emergency assistant.", "hi": "आप मुझे जार्विस कह सकते हैं। मैं आपका घरेलू आपातकालीन सहायक हूँ।", "kn": "ನೀವು ನನ್ನನ್ನು ಜಾರ್ವಿಸ್ ಎಂದು ಕರೆಯಬಹುದು. ನಾನು ನಿಮ್ಮ ಮನೆ ತುರ್ತು ಸಹಾಯಕ.", "ta": "நீங்கள் என்னை ஜார்விஸ் என்று அழைக்கலாம். நான் உங்கள் வீட்டு அவசர உதவியாளர்.", "te": "మీరు నన్ను జార్విస్ అని పిలవవచ్చు. నేను మీ ఇంటి అత్యవసర సహాయకుడిని.", "ml": "നിങ്ങൾക്ക് എന്നെ ജാർവിസ് എന്ന് വിളിക്കാം. ഞാൻ നിങ്ങളുടെ വീടിന്റെ അടിയന്തര സഹായിയാണ്."}
    },
    "functions": {
        "keywords": ["what can you do", "your purpose", "how do you help", "kya kar sakte ho"],
        "responses": {"en": "I can detect home emergencies and have a simple chat. If you are in danger, please describe the situation.", "hi": "मैं घरेलू आपात स्थितियों का पता लगा सकता हूँ और साधारण बातचीत कर सकता हूँ। यदि आप खतरे में हैं, तो कृपया स्थिति का वर्णन करें।", "kn": "ನಾನು ಮನೆ ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳನ್ನು ಪತ್ತೆ ಮಾಡಬಲ್ಲೆ ಮತ್ತು ಸರಳ ಚಾಟ್ ಮಾಡಬಲ್ಲೆ. ನೀವು ಅಪಾಯದಲ್ಲಿದ್ದರೆ, ದಯವಿಟ್ಟು ಪರಿಸ್ಥಿತಿಯನ್ನು ವಿವರಿಸಿ.", "ta": "நான் வீட்டு அவசரநிலைகளைக் கண்டறிந்து ஒரு எளிய அரட்டை அடிக்க முடியும். நீங்கள் ஆபத்தில் இருந்தால், தயவுசெய்து நிலைமையை விவரிக்கவும்.", "te": "నేను ఇంటి అత్యవసర పరిస్థితులను గుర్తించగలను మరియు సాధారణ చాట్ చేయగలను. మీరు ప్రమాదంలో ఉంటే, దయచేసి పరిస్థితిని వివరించండి.", "ml": "എനിക്ക് വീട്ടിലെ അടിയന്തര സാഹചര്യങ്ങൾ കണ്ടെത്താനും ലളിതമായ ചാറ്റ് നടത്താനും കഴിയും. നിങ്ങൾ അപകടത്തിലാണെങ്കിൽ, ദയവായി സാഹചര്യം വിവരിക്കുക."}
    },
    "farewell": {
        "keywords": ["bye", "goodbye", "see you", "alvida"],
        "responses": {"en": "Goodbye! Stay safe.", "hi": "अलविदा! सुरक्षित रहें।", "kn": "ವಿದಾಯ! ಸುರಕ್ಷಿತವಾಗಿರಿ.", "ta": "பிரியாவிடை! பாதுகாப்பாக இருங்கள்.", "te": "వీడ్కోలు! సురక్షితంగా ఉండండి.", "ml": "വിട! സുരക്ഷിതമായിരിക്കുക."}
    },
}

def get_hardcoded_response(user_input_en, lang='en'):
    user_input_en = user_input_en.lower().strip()
    for intent_data in hardcoded_intents.values():
        if any(keyword in user_input_en for keyword in intent_data["keywords"]):
            return intent_data["responses"].get(lang, intent_data["responses"]['en'])
    default_responses = {"en": "I am here to help with emergencies. Please describe the situation if you need assistance.", "hi": "मैं आपात स्थिति में मदद के लिए यहाँ हूँ। यदि आपको सहायता की आवश्यकता है तो कृपया स्थिति का वर्णन करें।", "kn": "ನಾನು ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳಲ್ಲಿ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ. ನಿಮಗೆ ಸಹಾಯ ಬೇಕಾದರೆ ದಯವಿಟ್ಟು ಪರಿಸ್ಥಿತಿಯನ್ನು ವಿವರಿಸಿ.", "ta": "அவசரநிலைகளுக்கு உதவ நான் இங்கே இருக்கிறேன். உங்களுக்கு உதவி தேவைப்பட்டால் நிலைமையை விவரிக்கவும்.", "te": "నేను అత్యవసర పరిస్థితులలో సహాయం చేయడానికి ఇక్కడ ఉన్నాను. మీకు సహాయం అవసరమైతే దయచేసి పరిస్థితిని వివరించండి.", "ml": "അടിയന്തര സാഹചര്യങ്ങളിൽ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്. നിങ്ങൾക്ക് സഹായം വേണമെങ്കിൽ ദയവായി സാഹചര്യം വിവരിക്കുക."}
    return default_responses.get(lang, default_responses['en'])

# -------------------------------
# Streamlit App UI & Logic
# -------------------------------
st.set_page_config(page_title="🏠 Home Emergency Assistant", layout="centered")
st.title("🏠 Multilingual Home Emergency Assistant")

if "messages" not in st.session_state: st.session_state.messages = []
if "speak_now" not in st.session_state: st.session_state.speak_now = None
if "alert_audio_played" not in st.session_state: st.session_state.alert_audio_played = False
if "call_in_progress" not in st.session_state: st.session_state.call_in_progress = False
if "call_completed" not in st.session_state: st.session_state.call_completed = False

st.session_state.tts_placeholder = st.empty()

if st.session_state.speak_now:
    utils.speak(st.session_state.speak_now["response"], st.session_state.speak_now["tip"], st.session_state.speak_now["lang"])
    st.session_state.speak_now = None

is_emergency_active = any(msg.get("role") == "alert" for msg in st.session_state.messages)

if not is_emergency_active:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]): st.markdown(message["content"])
else:
    alert_item = next((msg for msg in st.session_state.messages if msg["role"] == "alert"), None)
    if alert_item:
        data = alert_item['data']
        
        utils.speak(data["response"], data["tip"], data["lang"], autoplay=not st.session_state.alert_audio_played)
        st.session_state.alert_audio_played = True
        
        if data.get("triggering_input"): st.success(data["triggering_input"])
        col1, col2 = st.columns([1, 4])
        if data["icon"] and os.path.exists(data["icon"]):
            with col1: st.image(data["icon"], width=100)
        with col2:
            st.subheader(f"🚨 {data['emergency_type'].title()} Alert"); st.write(data["response"])
            if data["tip"]: st.info(f"💡 Safety Tip: {data['tip']}")
        
        # ✨ FIX: Your simple SMS button is back.
        if st.button("📩 Send Emergency SMS"):
            msg_to_send = f"EMERGENCY ALERT: {data['emergency_type'].title()}. {data['response']} {data['tip']}"
            if send_sms(msg_to_send):
                st.success("📩 Quick Alert sent to Discord!")
            else:
                st.error("❌ Failed to send Quick Alert.")

        # ✨ FIX: The panic button is now displayed below the simple SMS button.
        render_panic_button(data)


option = st.radio("Choose input method:", ["Text", "Voice"], key="input_option", horizontal=True)
user_input, detected_lang = "", "en"
if option == "Text":
    if prompt := st.chat_input("Describe your situation or ask a question..."):
        user_input = prompt
        detected_lang = utils.translator.detect(user_input).lang
else:
    if st.button("🎤 Press to Speak"):
        user_input, detected_lang = utils.get_voice_input()
        if user_input: st.session_state.last_user_input = f"You said: {user_input} ({detected_lang})"

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
                "emergency_type": emergency_type, "response": final_response, 
                "tip": final_tip, "icon": details["icon"], 
                "triggering_input": f"You said: {user_input} ({detected_lang})",
                "lang": detected_lang,
                "user": user_input 
            }
        }
        st.session_state.messages.append(alert_data)
        st.session_state.alert_audio_played = False
        st.rerun()
    else: # Casual Conversation
        if is_emergency_active: st.session_state.messages.clear()
        st.session_state.messages.append({"role": "user", "content": user_input})
        final_ai_response = get_hardcoded_response(english_text, detected_lang)
        st.session_state.messages.append({"role": "assistant", "content": final_ai_response})
        st.session_state.speak_now = {"response": final_ai_response, "tip": "", "lang": detected_lang}
        st.rerun()