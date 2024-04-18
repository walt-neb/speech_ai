from gtts import gTTS
import os
import speech_recognition as sr
from openai import OpenAI



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
        messages=[{"role": "system", "content": "You are a helpful assistant, who makes very brief responses."},
                  {"role": "user", "content": prompt}])
        # Extract the text from the response
        response_text = response.choices[0].message.content
        return response_text
    except Exception as e:
        return str(e)

def speak(text):
    tts = gTTS(text=text, lang='en')  # Initialize the gTTS with text
    tts.save("temp.mp3")  # Save the speech audio into a file
    os.system("mpg321 temp.mp3")  # Play the converted audio

def listen():
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()

    # Listening to the microphone and capture the audio
    with sr.Microphone() as source:
        print("Your turn to talk")
        audio_text = r.listen(source)
        print("Time over, thanks")
        try:
            # using google speech recognition
            recognized_audio_string = r.recognize_google(audio_text)
            speak("I heard, " + recognized_audio_string)
        except:
             speak("Sorry, I did not get that")
    return audio_text


def listen_and_recognize():
    # Initialize the recognizer
    r = sr.Recognizer()
    gpt_response = None

    # Define the microphone (uses default system microphone)
    with sr.Microphone() as source:
        # Calibrate the microphone to ambient noise
        print("Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=1)

        # Start the listening loop
        print("Listening...")
        while True:
            try:
                # Listen for the first phrase and extract it into audio data
                audio = r.listen(source)
                print("Recognizing...")

                # Use Google Web Speech API to recognize audio
                recognized_text = r.recognize_google(audio)
                if recognized_text == gpt_response:
                    recognized_text = None
                print(recognized_text)
                if recognized_text == "exit program":
                    speak("exiting program")
                    return

                else:
                    #response = input('would you like to send this text to gpt3.5? Y/n').lower()
                    if recognized_text != None:
                        gpt_response = query_gpt3_5(recognized_text)
                        recognized_text = '' #clear last voice input
                        print("GPT-3 response: " + gpt_response)
                        speak(gpt_response)


                # Here you could check the recognized text and perform actions or break the loop

            except sr.UnknownValueError:
                # Google Web Speech API could not understand audio
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                # Could not request results from Google Web Speech API
                print(f"Could not request results from Google Speech Recognition service; {e}")


if __name__ == '__main__':
    listen_and_recognize()

    # speak("Hello, I'm an audio enabled AI, how can I help you today?")
    # user_speach = listen()
    #
    # example_prompt = "What are some key advantages of Python over other programming languages?"
    #
    # gpt_response_string = query_gpt3_5(user_speach)
    # print("Response from GPT-3.5:", gpt_response_string)
    # speak(gpt_response_string)