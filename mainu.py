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
from llm_tools import AGENT_MUTED

# Assuming llm_callu is a function you have in a file named llm_calls.py

class VoiceAgent:
    """A voice controlled agent that listens, processes , and speaks."""

    def __init__(self):
        """Initializes the voice agent."""
        self.recognizer=sr.Recognizer()
        self.activation_phrase="luna start"
        self.termination_phrase="exit"

    @staticmethod
    def clean_text(text:str)->str:
        """Removes unwanted characters and symbols from text."""
        if isinstance(text, list):
            text = " ".join(text)
        text=re.sub(r"[*_`]","",text)# Remove markdown-like characters
        text=re.sub(r"[^\w\s.,!?']","",text) # Keep basic punctuation and words
        return text.strip()
    def speak(self,text:str)->None:
        """Converts text to speech and plays it without saving to a file.  """
        if not AGENT_MUTED:
            cleaned_text=self.clean_text(text)
            if not cleaned_text:
                print(colored("Skipping empty text for speech.","yellow"))
                return
            try:
                #1. Genrate speech with gTTs into an in-memory bytes buffer
                mp3_fp=io.BytesIO()
                tts=gTTS(text=cleaned_text,lang="en-IN",slow=False)
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)

                #2. Convert MP3 bytes to WAV bytes using pydub
                sound=AudioSegment.from_file(mp3_fp,format="mp3")
                wav_fp=io.BytesIO()
                sound.export(wav_fp,format="wav")
                wav_fp.seek(0)

                #3. Play the wav bytes using sounddevice
                data,samplerate=sf.read(wav_fp)
                sd.play(data,samplerate)
                sd.wait()
            except Exception as e:
                print(colored(f"Error in speak function: {e}","red"))
        else:
            print(colored("Agent is muted. Skipping speech output.","yellow"))

    def listen(self,source:sr.Microphone)->str:
        """Listens for audio input and converts it to text.
            this is a bloacking function use it in thread
        """
        print(colored("🎤 Listening......","cyan"))
        try:
            audio=self.recognizer.listen(source,timeout=10,phrase_time_limit=21)
            query=self.recognizer.recognize_google(audio)
            print(colored(f"you said: {query}","yellow"))
            return query.lower()
        except sr.WaitTimeoutError:
            print(colored(" ⏱️ Listening timed out while waiting for phrase to start","red"))
            return ""
        except sr.UnknownValueError:
            print(colored("❓ Sorry, I did not understand that.","red"))
            return ""
        except sr.RequestError as e:
            print(colored(f"Could not request results from Google Speech Recognition service; {e}","red"))
            return ""
    async def run(self)->None:
        """the main async loop to run the agent"""
        print(colored(f"Say {self.activation_phrase} to activate the agent","green"))
        with sr.Microphone() as source:
            #adjust for ambuent noise once  at the beginning
            print("Calibrating microphone.......")
            self.recognizer.adjust_for_ambient_noise(source,duration=1)
            print("Clibration complete.")
            #________Activation loop_______
            while True:
                query=self.listen(source)
                if self.activation_phrase in query:
                    await asyncio.to_thread(self.speak,"Luna agent activated.")
                    break
            #_____conversation loop_____
            while True:
                query=await asyncio.to_thread(self.listen,source)
                if not query:
                    continue
                if self.termination_phrase in query:
                    await asyncio.to_thread(self.speak,"Goodbye!.....")
                    break
                response= await asyncio.to_thread(llm_callu,query)
                print(colored(f"Luna: {response}","green"))
                #speak the response in a separted thread
                await asyncio.to_thread(self.speak,response)

if __name__=="__main__":
    banner=colored(pyfiglet.figlet_format("luna Agent"),"green")
    print(banner)
    print(colored("Made with 💖 by Shivanshu Prajapati","green"))
    agent = VoiceAgent()
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n"+colored("Agent interrupted by user  shutting down.","magenta"))







































