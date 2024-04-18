import os
import threading
from gtts import gTTS
import speech_recognition as sr
from openai import OpenAI
from datetime import datetime
from io import BytesIO
from pygame import mixer  # pygame library for playing audio from memory


# Here are the available engine strings for GPT-3.5 that you can use:
# text-davinci-002: This is the most capable version of the GPT-3.5 model. It offers the highest
# quality completions and is best suited for applications requiring a deep understanding of
# context or generating creative content.
# text-curie-001: This engine offers a good balance between cost and capability, suitable for
# tasks requiring understanding but not as depth-heavy as those best for Davinci.
# text-babbage-001: This model is faster and less expensive than Davinci and Curie, suitable for
# straightforward tasks that require less nuance.
# text-ada-001: This is the fastest and least expensive version of GPT-3.5, best used for tasks
# that can tolerate lower-quality completions or where speed is more critical than depth.

# Reset
Color_Off="\033[0m"       # Text Reset
# Regular Colors
Black="\033[0;30m"        # Black
Red="\033[0;31m"          # Red
Green="\033[0;32m"        # Green
Yellow="\033[0;33m"       # Yellow
Blue="\033[0;34m"         # Blue
Purple="\033[0;35m"       # Purple
Cyan="\033[0;36m"         # Cyan
White="\033[0;37m"        # White

# Initialize the mixer module
mixer.init()


def cprint(text, color):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[0;37m{current_time} {color}{text}\033[0m")

def speak(text):
    """ Play text to speech without saving to file. """
    tts = gTTS(text=text, lang='en')
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    mixer.music.load(buf)
    last_speech_output_time = time.time()
    mixer.music.play()

    while mixer.music.get_busy():  # wait for audio to finish playing
        pass

def query_gpt3_5(prompt, callback):
    """ Query GPT-3.5 and handle the response asynchronously. """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("API key not found.")
        return

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an audio enabled assistant, who provides brief responses."},
                      {"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content
        callback(response_text)
    except Exception as e:
        print(str(e))

def handle_gpt_response(response_text):
    """ Callback to handle GPT response. """
    cprint("GPT-3 response: " + response_text, Purple)
    speak(response_text)

def listen_and_recognize():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)  # Shorten calibration time
        print("Listening...")
        while True:
            try:
                audio = r.listen(source)
                recognized_text = r.recognize_google(audio)
                if recognized_text.lower() == "exit program":
                    cprint("Exiting program...", Red)
                    speak("Exiting program")
                    break
                cprint('User Input: ' + recognized_text, Blue)
                threading.Thread(target=query_gpt3_5, args=(recognized_text, handle_gpt_response)).start()
            except sr.UnknownValueError:
                cprint("Could not understand audio", Red)
            except sr.RequestError as e:
                cprint(f"Could not request results; {e}", Red)

if __name__ == '__main__':
    listen_and_recognize()
