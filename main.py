import re
import asyncio
import io
import os
import speech_recognition as sr
from termcolor import colored
import pyfiglet
from gtts import gTTS
from pydub import AudioSegment
import soundfile as sf
import sounddevice as sd
from llm_calls import llm_callu

# Assuming llm_callu is a function you have in a file named llm_calls.py
# from llm_calls import llm_callu

# Mock function for demonstration if llm_calls.py is not available

class VoiceAgent:
    """A voice-controlled agent that listens, processes, and speaks."""

    def __init__(self):
        """Initializes the voice agent."""
        self.recognizer = sr.Recognizer()
        self.activation_phrase = "luna start"
        self.termination_phrase = "exit"

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes unwanted characters and symbols from text."""
        text = re.sub(r"[*_`]", "", text)  # Remove markdown-like characters
        text = re.sub(r"[^\w\s.,!?']", "", text)  # Keep basic punctuation and words
        return text.strip()

    def speak(self, text: str) -> None:
        """
        Converts text to speech and plays it without saving to a file.
        This function is blocking and should be run in a separate thread.
        """
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            print(colored("Skipping empty text for speech.", "yellow"))
            return

        try:
            # 1. Generate speech with gTTS into an in-memory bytes buffer
            mp3_fp = io.BytesIO()
            #tts = gTTS(text=cleaned_text, lang='en', slow=False)
            tts = gTTS(text=cleaned_text, slow=False)
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            # 2. Convert MP3 bytes to WAV bytes using pydub
            sound = AudioSegment.from_file(mp3_fp, format="mp3")
            wav_fp = io.BytesIO()
            sound.export(wav_fp, format="wav")
            wav_fp.seek(0)

            # 3. Play the WAV bytes using sounddevice
            data, samplerate = sf.read(wav_fp)
            sd.play(data, samplerate)
            sd.wait()  # This blocks until the audio is done playing

        except Exception as e:
            print(colored(f"Error during text-to-speech: {e}", "red"))

    def listen(self, source: sr.Microphone) -> str:
        """
        Listens for user input from the microphone.
        This is a blocking function.
        """
        print(colored("🎤 Listening...", "cyan"))
        try:
            # Listen for audio input with a timeout
            audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=15)
            query = self.recognizer.recognize_google(audio)
            print(colored(f"You said: {query}", "yellow"))
            return query.lower()
        except sr.WaitTimeoutError:
            print(colored("⏱️ Listening timed out. Please try again.", "red"))
            return ""
        except sr.UnknownValueError:
            print(colored("❓ Could not understand audio.", "red"))
            return ""
        except sr.RequestError as e:
            print(colored(f"Could not request results; {e}", "red"))
            return ""

    async def run(self) -> None:
        """The main async loop to run the agent."""
        print(colored(f"Say '{self.activation_phrase}' to activate me...", "cyan"))

        with sr.Microphone() as source:
            # Adjust for ambient noise once at the beginning
            print("Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Calibration complete.")

            # --- Activation Loop ---
            while True:
                query = await asyncio.to_thread(self.listen, source)
                if self.activation_phrase in query:
                    await asyncio.to_thread(self.speak, "Luna agent activated.")
                    break

            # --- Conversation Loop ---
            while True:
                query = await asyncio.to_thread(self.listen, source)

                if not query:
                    continue  # If listening failed, loop again

                if self.termination_phrase in query:
                    await asyncio.to_thread(self.speak, "Goodbye, shutting down.")
                    break

                # Get LLM response in a separate thread
                response = await asyncio.to_thread(llm_callu, query)
                print(colored(f"Luna: {response}", "green"))

                # Speak the response in a separate thread
                await asyncio.to_thread(self.speak, response)


if __name__ == "__main__":
    banner = colored(pyfiglet.figlet_format("Luna Agent"), "green")
    print(banner)
    print(colored("Made with 💖 by Shivanshu Prajapati", "green"))

    agent = VoiceAgent()
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n" + colored("Agent interrupted by user. Shutting down.", "magenta"))






























    


























