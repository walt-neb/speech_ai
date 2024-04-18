import os
import json
import sounddevice as sd
import signal
import sys
from vosk import Model, KaldiRecognizer

def signal_handler(sig, frame):
    print('Stopping the script...')
    sys.exit(0)

def recognize_speech_from_microphone():
    model_path = "/home/walt/src/speach/vosk/vosk-model-en-us-0.22"  # Path to the Vosk model
    if not os.path.isdir(model_path):
        print(f"Model directory does not exist: {os.path.abspath(model_path)}")
        return

    try:
        model = Model(model_path)
    except Exception as e:
        print(f"Failed to load the model at {model_path}: {str(e)}")
        return

    recognizer = KaldiRecognizer(model, 16000)

    def callback(indata, frames, time, status):
        if status:
            print("Error:", status)
        if recognizer.AcceptWaveform(bytes(indata)):
            result = json.loads(recognizer.Result())
            if result and 'text' in result:
                print("Recognized:", result['text'])

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        print("Please speak now (press Ctrl+C to stop recording)...")
        signal.signal(signal.SIGINT, signal_handler)
        while True:
            pass  # Keep the stream alive

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    recognize_speech_from_microphone()
