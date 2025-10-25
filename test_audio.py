import sys

print("Python version:", sys.version)
print("\n" + "="*50)

# Test 1: Import PyAudio
print("\n1. Testing PyAudio import...")
try:
    import pyaudio
    print("✅ PyAudio imported successfully")
    print(f"   PyAudio version: {pyaudio.__version__}")
except Exception as e:
    print(f"❌ PyAudio import failed: {e}")
    sys.exit(1)

# Test 2: Initialize PyAudio
print("\n2. Testing PyAudio initialization...")
try:
    p = pyaudio.PyAudio()
    print(f"✅ PyAudio initialized")
    print(f"   Available audio devices: {p.get_device_count()}")
    
    # List devices
    print("\n   Audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"   [{i}] {info['name']} - Input channels: {info['maxInputChannels']}")
    
    p.terminate()
except Exception as e:
    print(f"❌ PyAudio initialization failed: {e}")
    sys.exit(1)

# Test 3: Import SpeechRecognition
print("\n3. Testing SpeechRecognition import...")
try:
    import speech_recognition as sr
    print("✅ SpeechRecognition imported successfully")
    print(f"   Version: {sr.__version__}")
except Exception as e:
    print(f"❌ SpeechRecognition import failed: {e}")
    sys.exit(1)

# Test 4: Test Microphone
print("\n4. Testing Microphone access...")
try:
    recognizer = sr.Recognizer()
    mic_list = sr.Microphone.list_microphone_names()
    print(f"✅ Found {len(mic_list)} microphone(s):")
    for i, name in enumerate(mic_list):
        print(f"   [{i}] {name}")
except Exception as e:
    print(f"❌ Microphone test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Quick recording test
print("\n5. Testing microphone recording (5 seconds)...")
print("   Say something now...")
try:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("   🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        print("   ✅ Recording successful!")
        
        # Try to recognize
        print("\n6. Testing speech recognition...")
        text = recognizer.recognize_google(audio)
        print(f"   ✅ Recognized: '{text}'")
        
except sr.WaitTimeoutError:
    print("   ⚠️  Timeout - no speech detected")
except sr.UnknownValueError:
    print("   ⚠️  Could not understand audio")
except Exception as e:
    print(f"   ❌ Recording failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("✅ All tests completed!")