import speech_recognition as sr
from googletrans import Translator
import sounddevice as sd
import soundfile as sf
from gtts import gTTS
from playsound import playsound
import streamlit as st

translator = Translator()

def get_voice_input(duration=5, fs=44100):
    """
    Record audio from microphone using sounddevice and return recognized text and language.
    """
    try:
        st.info(f"🎤 Listening for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        sf.write("temp.wav", recording, fs)
        recognizer = sr.Recognizer()
        with sr.AudioFile("temp.wav") as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        detected_lang = translator.detect(text).lang
        return text, detected_lang
    except Exception as e:
        print(e)
        return "", "en"

def speak(text, lang='en'):
    """
    Speak text in any language using gTTS.
    """
    if not text:
        return
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("response.mp3")
        playsound("response.mp3")
    except Exception as e:
        print(f"Error speaking: {e}")

def translate_text(text, dest='en'):
    """
    Translate text to the destination language. Handles empty text.
    """
    if not text:
        return ""
    try:
        return translator.translate(text, dest=dest).text
    except Exception as e:
        print(f"Translation error: {e}")
        return text
