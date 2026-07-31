import requests
import os

PIPER_HOST = os.getenv("PIPER_HOST", "http://piper:10200")

def synthesize_speech(text: str) -> bytes:
    response = requests.post(
        f"{PIPER_HOST}/api/tts",
        json={"text": text}
    )
    response.raise_for_status()
    return response.content   # raw audio bytes (wav format)