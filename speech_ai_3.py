import os
import json
from gtts import gTTS
from openai import OpenAI
from datetime import datetime
from io import BytesIO
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pygame import mixer  # pygame library for playing audio from memory
import time as tm


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
last_speech_output_time = 0

def cprint(text, color_code):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[{color_code}m{current_time}: {text}\033[0m")

def speak(text):
    global last_speech_output_time
    """ Play text to speech without saving to file. """
    tts = gTTS(text=text, lang='en')
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    mixer.music.load(buf)
    mixer.music.play()

    while mixer.music.get_busy():  # Wait for audio to finish playing
        pass
    last_speech_output_time = tm.time()  # Update the time after speaking


recent_responses = []
def query_gpt3_5(prompt):
    """ Query GPT-3.5 and handle the response asynchronously. """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        cprint("API key not found.", "31")  # Red text for errors
        return

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an audio enabled assistant, who provides brief responses."},
                      {"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content
        recent_responses.append(response_text)
        handle_gpt_response(response_text)
        if len(recent_responses) > 3:
            recent_responses.pop(0)

    except Exception as e:
        cprint(str(e), "31")


def handle_gpt_response(response_text):
    """ Callback to handle GPT response. """
    cprint("GPT-3 response: " + response_text, "35")  # Purple text
    speak(response_text)


def recognize_and_interact():
    model_path = "/home/walt/src/speach/vosk/vosk-model-en-us-0.22"  # Path to the Vosk model
    if not os.path.isdir(model_path):
        cprint(f"Model directory does not exist: {model_path}", "31")
        return

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    def callback(indata, frames, time, status):
        global last_speech_output_time
        if status:
            cprint(f"Status error: {status}", "31")
        if tm.time() - last_speech_output_time < 2.5:  # Check for time delay
            return  # Ignore this input

        if recognizer.AcceptWaveform(bytes(indata)):
            result = json.loads(recognizer.Result())
            if result and 'text' in result and result['text']:
                recognized_text = result['text'].strip()
                if recognized_text in recent_responses:
                    cprint("Skipping recognized text as it matches a recent response.", "33")  # Yellow for notices
                    return
                cprint("User: " + recognized_text, "34")  # Blue text
                query_gpt3_5(recognized_text)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        cprint("Please speak now (press Ctrl+C to stop recording)...", "32")  # Green text for system messages
        while True:
            pass  # Keep the stream alive

if __name__ == "__main__":
    recognize_and_interact()
