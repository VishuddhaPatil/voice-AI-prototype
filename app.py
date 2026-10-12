
import json
import queue
import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer
from ollama import chat

MODEL_PATH = "model"
SAMPLE_RATE = 16000

WAKE_WORD = "hey assistant"
END_WORDS = ["that's all", "thats all", "end request"]
EXIT_WORDS = [
    "goodbye assistant",
    "exit assistant",
    "quit assistant"
]

audio_queue = queue.Queue()

print("Loading offline speech recognition model...")
vosk_model = Model(MODEL_PATH)

print("Initializing speech...")
engine = pyttsx3.init()
engine.setProperty("rate", 170)

messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly voice assistant. "
            "Answer helpfully in simple language. "
            "Keep spoken answers reasonably short."
        )
    }
]


def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)
    audio_queue.put(bytes(indata))


def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


def get_ai_response(user_text):
    global messages

    messages.append({
        "role": "user",
        "content": user_text
    })

    try:
        response = chat(
            model="qwen2.5:1.5b",
            messages=messages
        )

        answer = response.message.content

        messages.append({
            "role": "assistant",
            "content": answer
        })

        if len(messages) > 13:
            messages = [messages[0]] + messages[-12:]

        return answer

    except Exception as error:
        print("AI error:", error)
        return "Sorry, I couldn't get an answer from my local AI model."


def main():
    recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
    active = False
    captured_words = []

    print("Starting offline voice assistant...")
    speak("Assistant ready. Say Hey Assistant to wake me up.")
    print("Standby: say 'Hey Assistant' to begin.")
    print("Say 'That's all' to finish a request.")
    print("Say 'Goodbye Assistant' to exit.")

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback
        ):
            while True:
                data = audio_queue.get()

                if not recognizer.AcceptWaveform(data):
                    continue

                result = json.loads(recognizer.Result())
                heard = result.get("text", "").strip().lower()

                if not heard:
                    continue

                print("Heard:", heard)

                # Always allow an exit phrase
                if any(word in heard for word in EXIT_WORDS):
                    speak("Goodbye! See you later.")
                    break

                # Wait for the wake word
                if not active:
                    if WAKE_WORD in heard:
                        active = True
                        captured_words = []

                        # Also capture anything spoken after the wake word
                        remainder = heard.split(WAKE_WORD, 1)[1].strip()
                        if remainder:
                            captured_words.extend(remainder.split())

                        speak("I'm listening.")
                    continue

                # Finish the current request
                end_word = next(
                    (word for word in END_WORDS if word in heard),
                    None
                )

                if end_word:
                    before_end = heard.split(end_word, 1)[0].strip()
                    if before_end:
                        captured_words.extend(before_end.split())

                    question = " ".join(captured_words).strip()
                    active = False
                    captured_words = []

                    if question:
                        print("You:", question)
                        answer = get_ai_response(question)
                        speak(answer)
                    else:
                        speak("I didn't hear a question. Say Hey Assistant to try again.")

                    print("Standby: say 'Hey Assistant' to begin.")
                    continue

                # Collect the request until an end phrase is detected
                captured_words.extend(heard.split())

    except KeyboardInterrupt:
        print("\nAssistant stopped.")

    except Exception as error:
        print("Error:", error)
        print("Check your model folder and microphone settings.")


if __name__ == "__main__":
    main()
