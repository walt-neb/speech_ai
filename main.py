
import asyncio
from gtts import gTTS
import os
import speech_recognition as sr
from openai import OpenAI
from datetime import datetime


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

def cprint(text, color):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\033[0;37m{current_time} {color}{text}\033[0m")


def query_gpt3_5(prompt):
    # Get the API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "API key not found."

    client = OpenAI(api_key=api_key)
    # Configure the library with your API key

    try:
        # Make an API call to the GPT-3.5 model using the new API interface
        response = client.chat.completions.create(model="gpt-3.5-turbo",  # Use this string for GPT-3.5
        messages=[{"role": "system", "content": "You are an audio enabled assistant, who provides brief responses."},
                  {"role": "user", "content": prompt}])
        # Extract the text from the response
        response_text = response.choices[0].message.content
        return response_text
    except Exception as e:
        return str(e)

def speak(text):
    tts = gTTS(text=text, lang='en')  # Initialize the gTTS with text
    tts.save("temp.mp3")  # Save the speech audio into a file
    os.system("mpg321 temp.mp3 >/dev/null 2>&1")  # Play the converted audio and suppress output



def listen_and_recognize():
    # Initialize the recognizer
    r = sr.Recognizer()
    gpt_response = None

    # Define the microphone (uses default system microphone)
    with sr.Microphone() as source:
        # Calibrate the microphone to ambient noise
        print("Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=2)

        intoduction_text = "Hello, I'm an audio enabled AI, at your service."
        print(intoduction_text)
        speak(intoduction_text)
        # Start the listening loop
        print("Listening...")
        while True:
            try:
                recognized_text = None
                # Listen for the first phrase and extract it into audio data
                audio = r.listen(source)
                cprint("Recognizing...", Red)
                recognized_text = r.recognize_google(audio) # Use Google Web Speech API to recognize audio
                cprint('Recognized text:'+ recognized_text, Red)
                cprint('User Input: ' + recognized_text, Blue)
                # check the recognized text and perform actions or break the loop
                if recognized_text == "exit program":
                    cprint("exiting program...", Red)
                    speak("exiting program")
                    return

                else:
                    #response = input('would you like to send this text to gpt3.5? Y/n').lower()
                    if recognized_text != None:
                        gpt_response = query_gpt3_5(recognized_text)
                        recognized_text = '' #clear last voice input
                        cprint("GPT-3 response: " + gpt_response, Purple)
                        speak(gpt_response)


            except sr.UnknownValueError:
                # Google Web Speech API could not understand audio
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                # Could not request results from Google Web Speech API
                print(f"Could not request results from Google Speech Recognition service; {e}")


if __name__ == '__main__':
    listen_and_recognize()

