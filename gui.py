
import json
import queue
import threading
import customtkinter as ctk
import sounddevice as sd
import pyttsx3

from vosk import Model, KaldiRecognizer
from ollama import chat


# ---------- Configuration ----------

MODEL_PATH = "model"
AI_MODEL = "qwen2.5:1.5b"
SAMPLE_RATE = 16000

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------- Main Application ----------

class VoiceAssistantApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Vox AI | Voice Assistant")
        self.geometry("900x680")
        self.minsize(650, 520)

        self.listening = False
        self.stop_event = threading.Event()
        self.audio_queue = queue.Queue()

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly voice assistant. "
                    "Give helpful answers in simple language. "
                    "Keep spoken answers reasonably short."
                )
            }
        ]

        self.build_ui()
        self.add_message(
            "assistant",
            "Hi! I'm Vox AI. Press the microphone button "
            "and ask me something."
        )

        self.status_label.configure(text="● Ready")

        self.protocol("WM_DELETE_WINDOW", self.close_app)

    # ---------- User Interface ----------

    def build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self, width=190, corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="◉  VOX AI",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(padx=20, pady=(30, 6), anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="YOUR PERSONAL ASSISTANT",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(padx=20, pady=(0, 28), anchor="w")

        ctk.CTkButton(
            self.sidebar,
            text="+  New conversation",
            command=self.new_conversation,
            height=40
        ).pack(padx=14, fill="x")

        ctk.CTkFrame(
            self.sidebar, height=2
        ).pack(fill="x", padx=14, pady=22)

        ctk.CTkLabel(
            self.sidebar,
            text="LOCAL AI",
            text_color="gray",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(padx=20, anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="●  Ollama + Qwen",
            text_color="#62D69B"
        ).pack(padx=20, pady=10, anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="●  Vosk speech",
            text_color="#62D69B"
        ).pack(padx=20, pady=5, anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="●  Local voice output",
            text_color="#62D69B"
        ).pack(padx=20, pady=5, anchor="w")

        # Main conversation area
        self.main_area = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.main_area.grid(
            row=0, column=1, sticky="nsew", padx=22, pady=18
        )
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self.main_area, fg_color="transparent"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="Your assistant",
            font=ctk.CTkFont(size=23, weight="bold")
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            header, text="● Loading...", text_color="gray"
        )
        self.status_label.pack(side="right", padx=5)

        # Scrollable conversation history
        self.history = ctk.CTkScrollableFrame(
            self.main_area,
            corner_radius=14,
            fg_color="#171B26"
        )
        self.history.grid(
            row=1, column=0, sticky="nsew", pady=(0, 15)
        )

        # Microphone controls
        controls = ctk.CTkFrame(
            self.main_area, fg_color="transparent"
        )
        controls.grid(row=2, column=0, sticky="ew")

        self.mic_button = ctk.CTkButton(
            controls,
            text="🎙  Start listening",
            height=48,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.toggle_listening
        )
        self.mic_button.pack(fill="x")

        ctk.CTkLabel(
            controls,
            text="Click to start listening. Click again to stop.",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        ).pack(pady=(8, 0))

    # ---------- Conversation History ----------

    def add_message(self, role, text):
        is_user = role == "user"

        row = ctk.CTkFrame(
            self.history, fg_color="transparent"
        )
        row.pack(fill="x", padx=10, pady=9)

        bubble = ctk.CTkFrame(
            row,
            fg_color="#244B82" if is_user else "#282E3B",
            corner_radius=14
        )
        bubble.pack(
            side="right" if is_user else "left",
            padx=(45, 0) if is_user else (0, 45)
        )

        ctk.CTkLabel(
            bubble,
            text="YOU" if is_user else "VOX AI",
            text_color="#A8CBFF" if is_user else "#70D6AE",
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w", padx=13, pady=(10, 2))

        ctk.CTkLabel(
            bubble,
            text=text,
            justify="left",
            anchor="w",
            wraplength=490,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=13, pady=(2, 12))

        self.after(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.history._parent_canvas.yview_moveto(1.0)

    def new_conversation(self):
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly voice assistant. "
                    "Answer in simple language and keep spoken "
                    "answers reasonably short."
                )
            }
        ]

        for widget in self.history.winfo_children():
            widget.destroy()

        self.add_message(
            "assistant", "New conversation started. What can I help with?"
        )

    # ---------- Microphone ----------

    def toggle_listening(self):
        if self.listening:
            self.stop_event.set()
            self.listening = False
            self.mic_button.configure(text="🎙  Start listening")
            self.status_label.configure(text="● Stopping...")
            return

        self.stop_event = threading.Event()
        self.listening = True

        self.mic_button.configure(
            text="■  Stop listening",
            fg_color="#B83B4B",
            hover_color="#96303D"
        )
        self.status_label.configure(
            text="● Listening...", text_color="#62D69B"
        )

        threading.Thread(
            target=self.listen_worker,
            daemon=True
        ).start()

    def listen_worker(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 170)

            while not self.stop_event.is_set():
                recognizer = KaldiRecognizer(
                    self.vosk_model, SAMPLE_RATE
                )
                audio_queue = queue.Queue()
                recognized_text = ""

                def audio_callback(
                    indata, frames, time_info, status
                ):
                    audio_queue.put(bytes(indata))

                # Close the microphone stream after each utterance.
                # This prevents most assistant-speech feedback.
                with sd.RawInputStream(
                    samplerate=SAMPLE_RATE,
                    blocksize=8000,
                    dtype="int16",
                    channels=1,
                    callback=audio_callback
                ):
                    while not self.stop_event.is_set():
                        try:
                            data = audio_queue.get(timeout=0.2)
                        except queue.Empty:
                            continue

                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            recognized_text = result.get(
                                "text", ""
                            ).strip()

                            if recognized_text:
                                break

                if self.stop_event.is_set():
                    break

                if not recognized_text:
                    continue

                self.after(
                    0, self.add_message, "user", recognized_text
                )

                self.messages.append({
                    "role": "user",
                    "content": recognized_text
                })

                self.after(
                    0, self.status_label.configure,
                    {"text": "● Thinking...", "text_color": "#E7BD68"}
                )

                try:
                    response = chat(
                        model=AI_MODEL,
                        messages=self.messages
                    )
                    answer = response.message.content

                except Exception as error:
                    print("Ollama error:", error)
                    answer = (
                        "I couldn't connect to the local AI. "
                        "Please check that Ollama is running "
                        "and your Qwen model is installed."
                    )

                self.messages.append({
                    "role": "assistant",
                    "content": answer
                })

                if len(self.messages) > 13:
                    self.messages = (
                        [self.messages[0]] + self.messages[-12:]
                    )

                self.after(
                    0, self.add_message, "assistant", answer
                )

                if self.stop_event.is_set():
                    break

                self.after(
                    0, self.status_label.configure,
                    {"text": "● Speaking...", "text_color": "#62D69B"}
                )

                engine.say(answer)
                engine.runAndWait()

            engine.stop()

        except Exception as error:
            print("Voice error:", error)
            self.after(
                0, self.add_message, "assistant",
                "I encountered a microphone or voice error. "
                "Check your microphone settings and try again."
            )

        finally:
            self.after(0, self.worker_stopped)

    def worker_stopped(self):
        self.listening = False
        self.mic_button.configure(
            text="🎙  Start listening",
            fg_color="#1F6AA5",
            hover_color="#144870"
        )
        self.status_label.configure(
            text="● Ready", text_color="gray"
        )

    def close_app(self):
        self.stop_event.set()
        self.destroy()


# ---------- Launch ----------

if __name__ == "__main__":
    print("Loading Vosk model...")
    model = Model(MODEL_PATH)

    app = VoiceAssistantApp()
    app.vosk_model = model

    app.mainloop()
