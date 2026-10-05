import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import re

# ----------------------------
# TTS ENGINE SETUP & CLARITY SETTINGS
# ----------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
current_voice_idx = 0

if voices:
    engine.setProperty('voice', voices[current_voice_idx].id)

speech_rate = 160  # Clear and articulate speaking rate
speech_volume = 1.0

engine.setProperty('rate', speech_rate)
engine.setProperty('volume', speech_volume)


def speak(text):
    """
    Speaks the provided text clearly and displays speaker output.
    """
    print(f"\n[Nova]: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech error: {e}")


def set_speaker_voice(index):
    """
    Modifies the speaker voice (e.g., switches between available voices).
    """
    global current_voice_idx
    if voices and 0 <= index < len(voices):
        current_voice_idx = index
        engine.setProperty('voice', voices[current_voice_idx].id)
        speak(f"Speaker voice changed to {voices[current_voice_idx].name}")
    else:
        speak("Voice option not available.")


def modify_speech_rate(delta):
    """
    Modifies speaker speed/clarity rate.
    """
    global speech_rate
    speech_rate = max(100, min(250, speech_rate + delta))
    engine.setProperty('rate', speech_rate)
    speak(f"Speaking rate set to {speech_rate} words per minute.")


# ----------------------------
# NOISE-CANCELING LISTEN FUNCTION
# ----------------------------

def clean_speaker_words(raw_text):
    """
    Cleans up and normalizes speaker words to ensure clear command processing.
    """
    if not raw_text:
        return ""
    
    cleaned = raw_text.lower().strip()
    
    # Remove common filler words & punctuation for better command recognition
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    filler_words = ["please", "could you", "can you", "hey nova", "nova"]
    for filler in filler_words:
        cleaned = cleaned.replace(filler, "").strip()
        
    return cleaned


def listen():
    """
    Listens for audio input, calibrates for background noise, and recognizes speech.
    """
    recognizer = sr.Recognizer()
    
    # Noise cancellation settings
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300  # Filters out background static/fan noise
    recognizer.pause_threshold = 0.8    # Responds promptly when speech stops
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5
    
    with sr.Microphone() as source:
        print("\n[Status]: Calibrating background noise... Please wait.")
        # Clear background noise by sampling ambient audio for 1 second
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("[Status]: Listening for your command (Background noise filtered)...")
        
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return ""

    try:
        raw_command = recognizer.recognize_google(audio, language="en-in")
        print(f"[User Spoke]: \"{raw_command}\"")
        command = clean_speaker_words(raw_command)
        print(f"[Processed Command]: \"{command}\"")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I could not hear clearly due to noise or unclear speech. Please speak again.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service is currently unreachable.")
        return ""


# ----------------------------
# PROCESS COMMAND LOOP
# ----------------------------

def main():
    speak("Hello! I am your Voice Assistant. Background noise reduction is active. How can I help you today?")
    
    while True:
        command = listen()
        if not command:
            continue

        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {current_time}")

        elif "date" in command:
            today = datetime.datetime.now().strftime("%d %B %Y")
            speak(f"Today's date is {today}")

        elif "open google" in command:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")

        elif "open youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

        elif "open gmail" in command:
            speak("Opening Gmail")
            webbrowser.open("https://mail.google.com")

        elif "open chat gpt" in command or "open chatgpt" in command or "open chat g p t" in command:
            speak("Opening ChatGPT")
            webbrowser.open("https://chatgpt.com")

        elif "your name" in command:
            speak("My name is Nova. I am your personal voice assistant.")

        elif "hello" in command or "hi" in command:
            speak("Hello! How can I assist you?")

        elif "who created you" in command:
            speak("I was created using Python and Speech Recognition with background noise cancellation.")

        elif "change voice" in command or "switch voice" in command:
            new_idx = (current_voice_idx + 1) % len(voices) if voices else 0
            set_speaker_voice(new_idx)

        elif "speak faster" in command or "faster" in command:
            modify_speech_rate(20)

        elif "speak slower" in command or "slower" in command:
            modify_speech_rate(-20)

        elif "bye" in command or "exit" in command or "stop" in command:
            speak("Goodbye! Have a wonderful day.")
            break

        elif "locate" in command or "map" in command:
            speak("Which place would you like to locate?")
            place = listen()
            if place:
                speak(f"Locating {place} on Google Maps")
                url = f"https://www.google.com/maps/search/{place}"
                webbrowser.open(url)

        elif "play" in command:
            song = command.replace("play", "").strip()
            if song:
                speak(f"Searching and playing {song} on YouTube")
                webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            else:
                speak("What song or video would you like to play?")

        elif "who is" in command or "what is" in command:
            query = command.replace("who is", "").replace("what is", "").strip()
            if query:
                try:
                    info = wikipedia.summary(query, sentences=2)
                    speak(info)
                except Exception:
                    speak(f"Sorry, I couldn't find detailed information for {query}.")
            else:
                speak("Please specify what you would like to search for.")

        elif "weather" in command:
            speak("Which city's weather would you like to check?")
            city = listen()
            if city:
                speak(f"Checking weather for {city}")
                webbrowser.open(f"https://www.google.com/search?q=weather+{city}")

        else:
            speak("I didn't quite catch that command. Could you please rephrase?")


if __name__ == "__main__":
    main()

