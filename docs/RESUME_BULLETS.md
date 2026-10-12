# Resume bullets — VOX AI Voice Assistant

Use the bullets that accurately match the version you have tested. Keep the project name and stack consistent with the code in your public repository.

## Recommended version

**VOX AI — Local Voice Assistant | Python, Vosk, Ollama, Qwen, CustomTkinter, pyttsx3**

- Built a Python desktop voice assistant that converts microphone speech to text with Vosk, generates responses using a locally hosted Qwen 2.5 model through Ollama, and speaks replies using `pyttsx3`.
- Developed a CustomTkinter GUI with microphone start/stop controls and a conversation-history view to make the assistant easier to interact with.
- Integrated local speech recognition and local LLM inference to reduce reliance on cloud-based AI services; documented environment setup, model installation, and troubleshooting for reproducibility.

## Short version for a one-page resume

- Developed a Python voice assistant using Vosk, Ollama (Qwen 2.5 1.5B), and `pyttsx3`, with a CustomTkinter GUI for microphone control and chat history.

## Optional metrics — add only after measuring

If you test the app, you can add factual measurements such as average response time, successful transcription rate across a fixed test set, or memory usage. Do not invent performance numbers.

## Interview talking points

Be ready to explain:
1. Why Vosk was chosen for local speech recognition.
2. How the app passes recognized text to Ollama and handles model responses.
3. How microphone capture, speech recognition, response generation, and text-to-speech are coordinated.
4. What limitations you observed (for example, noise, endpoint detection, latency, or hardware constraints).
5. What you would improve next (tests, device selection, error handling, and conversation state).
