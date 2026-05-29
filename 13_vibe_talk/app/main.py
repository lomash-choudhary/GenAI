import base64
import os
from openai.helpers import LocalAudioPlayer
import speech_recognition as sr
from .graph import graph
from openai import AsyncOpenAI
import asyncio

openai = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

messages=[]

async def tts(text: str):
    response = await openai.chat.completions.create(
        model="gemini-3.1-flash-tts-preview",
        messages=[{"role": "user", "content": text}],
        modalities=["audio"],                # Required for Gemini TTS models
        audio={
            "voice": "coral",                # Choose a valid voice name
            "format": "wav"               # Gemini TTS requires PCM16 format
        }
    )
    # The API returns audio data (likely base64-encoded PCM). Extract it from the response:
    audio_base64 = response.choices[0].message.audio.data
    audio_bytes = base64.b64decode(audio_base64)
    # return audio_data
    await LocalAudioPlayer().play(audio_bytes)

def main():
    r = sr.Recognizer() # this r is the speech recognizer variable, this converts speech to text on device

    
    with sr.Microphone() as source: # this will take the access of the user microphone and this is the mic access
        r.adjust_for_ambient_noise(source) # this removes the background noise on device.
        r.pause_threshold = 2 # if the user stops talking for 2 seconds then stop otherwise keep on listening to the user.
        while True:
            print("Speak something")
            audio = r.listen(source)

            print("Processing Audio... (speech to text)")
            stt = r.recognize_google(audio) # this will work on, for free other models will require api key

            print("You said:", stt)
            messages.append({"role":"user", "content":stt})

            for event in graph.stream({"messages": messages}, stream_mode="values"):
                if "messages" in event:
                    messages.append({"role":"user", "content":event["messages"][-1].content})
                    event["messages"][-1].pretty_print()



# main()
asyncio.run(tts(text="Hello my name is lomash"))