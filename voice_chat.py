import whisper
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

whisper_model = whisper.load_model("small")


def stt(filepath: str) -> str:
    response = whisper_model.transcribe(filepath, fp16=False)
    return response["text"]


def tts(text: str, voice: str = "alloy", isDeployed: bool = False):
    # voices = [alloy, echo, fable, onyx, nova, shimmer]
    response = client.audio.speech.create(
        model = "tts-1",
        voice=voice,
        input=text
    )
    
    if not isDeployed:
        with open("output.mp3", "wb") as f:
            f.write(response.read())
        
    return response.read()


if __name__ == "__main__":
    text = stt("input.wav")
    tts(text, "nova")