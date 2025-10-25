import speech_recognition as sr
from googletrans import Translator
import streamlit as st
import edge_tts
import asyncio
import tempfile
import base64
import os

translator = Translator()

def get_voice_input():
    try:
        st.info(f"🎤 Listening... Speak now.")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=20)
        text = recognizer.recognize_google(audio)
        detected_lang = translator.detect(text).lang
        return text, detected_lang
    except sr.UnknownValueError:
        st.warning("Could not understand your voice. Please try again.")
        return "", "en"
    except Exception as e:
        st.error(f"An error occurred during voice input: {e}")
        return "", "en"

# This function contains the one-line fix
async def _edge_speak_async(text, lang="en", autoplay=True):
    placeholder = st.session_state.get("tts_placeholder")
    if not text or not placeholder: return
    voice_map = {"en": "en-US-JennyNeural", "hi": "hi-IN-SwaraNeural", "fr": "fr-FR-DeniseNeural", "es": "es-ES-ElviraNeural", "de": "de-DE-KatjaNeural", "ta": "ta-IN-PallaviNeural", "kn": "kn-IN-SapnaNeural", "ml": "ml-IN-SobhanaNeural", "te": "te-IN-ShrutiNeural"}
    voice = voice_map.get(lang, "en-US-JennyNeural")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp: tmp_path = tmp.name
        communicate = edge_tts.Communicate(text, voice=voice, rate="+10%", volume="+5%")
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f: audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        
        autoplay_str = "autoplay" if autoplay else ""
        
        # ✨ FIX: The 'controls' attribute is removed and style is set to 'display:none' to hide the player.
        audio_html = f'<audio {autoplay_str} style="display:none;"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
        
        placeholder.empty(); placeholder.markdown(audio_html, unsafe_allow_html=True)
        os.remove(tmp_path)
    except Exception as e: st.error(f"Speech error: {e}")

def speak(text, tip="", lang="en", autoplay=True):
    if not text: return
    combined = text + (f". Safety tip: {tip}" if tip else "")
    try:
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(_edge_speak_async(combined, lang=lang, autoplay=autoplay))
        loop.close()
    except Exception as e: st.error(f"TTS loop error: {e}")

def translate_text(text, dest='en'):
    if not text: return ""
    try:
        return translator.translate(text, dest=dest).text
    except Exception as e:
        print(f"Translation error: {e}")
        return text